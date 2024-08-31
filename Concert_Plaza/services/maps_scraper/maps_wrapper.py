import datetime
import re
from urllib.parse import quote_plus
from time import sleep

import httpx
from bs4 import BeautifulSoup
from phonenumbers import is_possible_number, parse
from phonenumbers.phonenumberutil import country_code_for_region
from pydantic import HttpUrl

import constants
from exceptions import NoLocationException, NoSearchTermException, FailedToGetURL, CompanyNameNotFoundError
from schemas.depends import ISO31661Alfa2Enum
from schemas.maps_scraper.google_business_category import GoogleBusinessCategory
from schemas.maps_scraper.maps_html_identifiers import HtmlMapsClasses, HtmlMapsIds
from services.depends import WebWrapper
from services.maps_scraper.depends import valid_http_url, delete_duplicates_from_list, abbreviated_number_to_int
from schemas.maps_scraper.company import Company


class GoogleMapsWebWrapper(WebWrapper):
    """Google Maps Web Wrapper"""

    def __init__(self, timeout: float = 10.0, proxies: dict | None = None):
        """
        Create the class, define the typing and set default values for all attributes
        :param timeout: Set the timeout time for all the requests. Default 10s
        """
        super().__init__(timeout=timeout, proxies=proxies)
        self.base_url: str = str(constants.GOOGLE_URL)
        self.search_id: str | None = None
        self.user_id: str | None = None
        self.country: ISO31661Alfa2Enum | None = None
        self.city: str | None = None
        self.business_category: GoogleBusinessCategory | None = None
        self.country_phone_code: str | None = None
        self.campaign_id: str | None = None

    def set_location_args(self, country: ISO31661Alfa2Enum, city: str):
        try:
            self.country = country
            self.city = city
        except ValueError:
            raise ValueError('Incorrect country value in location args')
        
    def set_campaign(self, campaign_id: str):
        try:
            self.campaign_id = campaign_id
        except ValueError:
            raise ValueError('Incorrect campaign_id value in set campaign args')

    def generate_search_url(self, business_category: GoogleBusinessCategory | None, *args: str) -> HttpUrl:
        """
        Generates the url to scrape
        :param business_category: the thing to search
        :param args: info about the location must be at least two (like city, state or country)
        :returns: a correct url http to scrape. Validated by pydantic
        :raises NoLocationException: When the location info is less than two elements
        :raises NoSearchTermException: When the search_term is ''
        """
        if len(args) < 1:
            raise NoLocationException(f'There are no location args. Use minimum 1')
        if not business_category:
            raise NoSearchTermException('The search_term can\'t be empty')
        self.business_category = business_category
        self.country_phone_code = f'+{str(country_code_for_region(self.country.name))}'
        args = ([arg.casefold() for arg in args if arg.casefold() != self.country.casefold()]
                + [self.country.casefold()])
        search_term_with_location: str = '/search?q=' + quote_plus(f'{business_category.value} {" ".join(args)}')
        generated_search_url: HttpUrl = self.base_url + search_term_with_location + '&rlst=f#rlfi=hd'
        return generated_search_url

    def scrape_maps(self, url: HttpUrl):
        """
        Scrapes the requested google_maps url and the next pages in that page if exists
        :param url: a Google Maps url to scrape. Validated by pydantic
        :return:
        :raises FailedToGetURL: when can't access the requested url
        """
        url = str(url)
        try:
            response = self.client.get(url, headers=self.headers)
        except httpx.HTTPError as e:
            print('\n\nERROR GETTING URL. CHECK IP BLOCK\n\n\n')
            raise FailedToGetURL(e)
        soup = BeautifulSoup(response.content, features='lxml')
        next_btn = soup.find(id=HtmlMapsIds.NEXT_BTN)
        if next_btn:
            sleep(2)
            self.scrape_maps(self.base_url + next_btn['href'])

        for result in soup.find_all(name='div', class_=HtmlMapsClasses.RESULTS):
            try:
                scrapped_elements = self._transform_results(self._extract_results(beautiful_soup_object=result))

                self.scraped_companies.companies_list.append(
                    Company(
                        search_id = self.search_id,
                        user_id=self.user_id,
                        name=scrapped_elements['company_name'],
                        country=self.country,
                        city=self.city,
                        date=datetime.datetime.now(),
                        business_category=self.business_category,
                        score=scrapped_elements['score'],
                        number_of_opinions=scrapped_elements['number_of_opinions'],
                        address=scrapped_elements['address'],
                        phone_number=scrapped_elements['phone_number'],
                        website=scrapped_elements['website'],
                        campaign_id=self.campaign_id
                    )
                )
            except (ValueError, CompanyNameNotFoundError) as e:
                if isinstance(e, CompanyNameNotFoundError):
                    print('Company name not found. Check element search in html')  # Critical error
                if isinstance(e, ValueError):
                    print(f'Error reading company: {e}')

    def remove_duplicates_in_data(self):
        """
        Remove the duplicated elements in companies list attribute. Two elements in the list are considered duplicated
        when all keys have the same value
        """
        self.scraped_companies.companies_list = delete_duplicates_from_list(self.scraped_companies.companies_list)

    @staticmethod
    def _extract_results(beautiful_soup_object: BeautifulSoup) -> dict:
        """
        Search the web elements to scrape and saves them to a dict
        :param beautiful_soup_object: A BeautifulSoup object with a company info
        :return: dict of BeautifulSoup or None objects
        """
        return dict(
            company_name=beautiful_soup_object.find('div', class_=HtmlMapsClasses.COMPANY_NAME),
            score=beautiful_soup_object.find('span', class_=HtmlMapsClasses.SCORE),
            number_of_opinions=beautiful_soup_object.find('span', class_=HtmlMapsClasses.NUMBER_OF_OPINIONS),
            details=beautiful_soup_object.find('div', class_=HtmlMapsClasses.DETAILS),
            website=beautiful_soup_object.find('a', class_=HtmlMapsClasses.WEBSITE, href=True),
        )

    def _transform_results(self, scrapped_results: dict) -> dict:
        """
        validate and remap scraped data to correspond to Company schema
        :param scrapped_results: a dict with BeautifulSoup or None objects
        :return: dict with values corresponding to Company schema
        """
        # company name validations
        if not scrapped_results['company_name']:
            raise CompanyNameNotFoundError
        scrapped_results['company_name'] = scrapped_results['company_name'].text

        # score validations
        scrapped_results['score'] = (float(scrapped_results['score'].text.replace(',', '.'))
                                     if scrapped_results['score'] else None)

        # number of opinions validations
        scrapped_results['number_of_opinions'] = (scrapped_results['number_of_opinions'].text[1:-1]
                                                  if scrapped_results['number_of_opinions'] else None)
        scrapped_results['number_of_opinions'] = abbreviated_number_to_int(scrapped_results['number_of_opinions'])

        # address
        try:
            address_first_filter = (re.search(r'[\w \-]+.?\s?\d{0,3}\s?#\d{1,3}[a-zA-Z]?\s?-\s?\d{1,3}',
                                              scrapped_results['details'].text) if scrapped_results[
                'details'] else None)[0]
            address_second_filter = (re.search(r'(Cra|Cl).?\s?\d{0,3}\s?#\d{1,3}[a-zA-Z]?\s?-\s?\d{1,3}',
                                               address_first_filter) if address_first_filter else None)
            scrapped_results['address'] = address_second_filter[0] if address_second_filter else address_first_filter
        except TypeError:
            scrapped_results['address'] = None

        # phone number validations
        try:
            phone_number = (re.search(r'\d{2}-? ?\d{3}-? ?\d{7}|\d{3} \d{7}|\(\d{3}\) \d{7}', scrapped_results['details'].text)
                            if scrapped_results['details'] else None)
            phone_number = (phone_number[0].replace(' ', '')
                            .replace('(', '').replace(')', '').replace('-','')) if phone_number else None
            phone_number = f'{self.country_phone_code}{phone_number}' if phone_number else None
            possible_number = is_possible_number(parse(phone_number)) if phone_number else False
            scrapped_results['phone_number'] = phone_number if possible_number else None
        except TypeError:
            scrapped_results['phone_number'] = None

        # website validations
        try:
            scrapped_results['website'] = (scrapped_results['website']['href']
                                           if scrapped_results['website'] else None)
            scrapped_results['website'] = (self.base_url + scrapped_results['website']
                                           if str(scrapped_results['website']).startswith('/')
                                           else scrapped_results['website'])
            scrapped_results['website'] = (scrapped_results['website']
                                           if valid_http_url(scrapped_results['website']) else None)
        except ValueError:
            scrapped_results['website'] = None

        return scrapped_results
