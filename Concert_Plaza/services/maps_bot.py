from schemas.maps_scraper.google_business_category import GoogleBusinessCategory
from schemas.maps_scraper.location_args import LocationArgs
from schemas.depends import ISO31661Alfa2Enum
#from services.aws_kinesis_eliminar.send_data_to_kinesis import batch_stream_to_firehose
from services.maps_scraper.depends import merge_location_args
from services.maps_scraper.maps_wrapper import GoogleMapsWebWrapper
from services.landing_scrapper.wraper import LandingWebWrapper
import json
import os


def maps_bot(business_category: GoogleBusinessCategory, location_args: LocationArgs, campaign_id = str | None):
    """
    Apply web scraping to find all companies in a defined location
    :param business_category: the thing to search (Google Business Categories)
    :param location_args: specific location information
    """
    args = merge_location_args(location_args)
    maps = GoogleMapsWebWrapper()
    maps.set_location_args(country=location_args.country, city=location_args.city)
    maps.set_campaign(campaign_id=campaign_id)
    search_url = maps.generate_search_url(business_category, *args)
    maps.scrape_maps(search_url)
    maps.remove_duplicates_in_data()
    maps.close_client()
    landing = LandingWebWrapper(companies = maps.scraped_companies)
    landing.scrape_landing_pages()
    print(f'{len(landing.scraped_companies.companies_list)} companies found')
    print(landing.scraped_companies.companies_list)



def search_by_country(country: ISO31661Alfa2Enum, campaign_id = str | None):
    """
    Run maps_scraper_bot in the five most populated cities in each state of a country.
    :param country: Object of ISO31661Alfa2Enum class
    Demographic information for each city was obtained from: https://public.opendatasoft.com/explore/dataset/geonames-all-cities-with-a-population-1000/
    """
    # Load json files
    countries_json, cities_json = load_files(country)
    if cities_json:
        for state in countries_json:  # Iterate over states of the country
            all_cities = [cities['name'].replace(' D.C.', '') for cities in
                          state['cities']]  # Get all cities in the state
            important_cities = order_cities(all_cities_found=all_cities, list_dict_cities=cities_json)[0:5]
            if important_cities:
                for city in important_cities:
                    for business_category in GoogleBusinessCategory:
                        maps_bot(
                            business_category=GoogleBusinessCategory[business_category],
                            location_args=LocationArgs(
                                city=city,
                                state=state["name"],
                                country=country.value
                            ),
                            campaign_id=campaign_id
                        )
            else:
                print(f'No relevant cities found in {state["name"]}')
    else:
        print('Try another country.')


def load_files(country: ISO31661Alfa2Enum):
    """
    Load json files
    :returns: a tuple with the information loaded from the json files
    """
    files_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "files"))
    with open(files_path + '/countries_plus_states_plus_cities.json', 'r') as f:
        countries_json = json.load(f)
    with open(files_path + '/geonames-all-cities-with-a-population-1000.json', 'r') as f:
        cities_json = json.load(f)
    # get general information about the country (dictionary)
    countries_json = next(iter([
        country_info['states'] for country_info in countries_json if (country_info["iso2"] == country.name)]), None)
    # get general information about the cities of the country (dictionary list)
    cities_json = [city_info for city_info in cities_json if (city_info["country_code"] == country.name)]
    return countries_json, cities_json


def order_cities(all_cities_found: list, list_dict_cities: list):  # Order cities by its population
    """
    Get a list of cities ordered by population
    :param all_cities_found: List of all cities in a state
    :param list_dict_cities: List of the cities with demographic information
    :returns: a list of city names ordered from most populated to the least populated
    """
    cities_found = []
    for city in list_dict_cities:
        if city['alternate_names']:
            names = city['alternate_names']
            names.append(city['name'])
        else:
            names = [city['name']]
        if bool(set(all_cities_found) & set(names)):
            cities_found.append(city)
    if cities_found:
        cities_found.sort(key=lambda city_: city_["population"], reverse=True)
        ordered_names = [city["name"] for city in cities_found]
        return ordered_names
    else:
        return []
