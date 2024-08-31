import os
import sys
from unittest.mock import patch

import httpx
import pytest
from aioresponses import aioresponses
from fastapi.testclient import TestClient
from phonenumbers.phonenumberutil import country_code_for_region

# Add the absolute path to the app folder to the sys.path list.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from exceptions import NoSearchTermException, NoLocationException
from routers.maps_scraper.maps_scraper import router
from schemas.depends import ISO31661Alfa2Enum
from schemas.maps_scraper.google_business_category import GoogleBusinessCategory
from schemas.maps_scraper.location_args import LocationArgs
from services.maps_bot import load_files, order_cities, search_by_country
from services.maps_scraper.depends import abbreviated_number_to_int, delete_duplicates_from_list
from services.maps_scraper.depends import merge_location_args
from services.maps_scraper.maps_wrapper import GoogleMapsWebWrapper


# _________Load files test___________
Colombia_states = ['Amazonas', 'Antioquia', 'Arauca', 'Archipiélago de San Andrés, Providencia y Santa Catalina',
                   'Atlántico', 'Bogotá D.C.', 'Bolívar', 'Boyacá', 'Caldas', 'Caquetá', 'Casanare', 'Cauca', 'Cesar',
                   'Chocó', 'Córdoba', 'Cundinamarca', 'Guainía', 'Guaviare', 'Huila', 'La Guajira', 'Magdalena',
                   'Meta', 'Nariño', 'Norte de Santander', 'Putumayo', 'Quindío', 'Risaralda', 'Santander', 'Sucre',
                   'Tolima', 'Valle del Cauca', 'Vaupés', 'Vichada']
Ecuador_states = ['Azuay', 'Bolívar', 'Cañar', 'Carchi', 'Chimborazo', 'Cotopaxi', 'El Oro', 'Esmeraldas', 'Galápagos',
                  'Guayas', 'Imbabura', 'Loja', 'Los Ríos', 'Manabí', 'Morona-Santiago', 'Napo', 'Orellana', 'Pastaza',
                  'Pichincha', 'Santa Elena', 'Santo Domingo de los Tsáchilas', 'Sucumbíos', 'Tungurahua',
                  'Zamora Chinchipe']


@pytest.mark.parametrize(
    'cwd,ctry,exp_state',
    [
        (os.path.abspath(os.path.join(os.path.dirname(__file__), "..")),
         ISO31661Alfa2Enum.CO,
         Colombia_states
         ),
        (os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")),
         ISO31661Alfa2Enum.EC,
         Ecuador_states
         )
    ]
)
def test_load_files(cwd, ctry, exp_state):
    """
    Check if the function to load files is robusts to current working directory
    :param cwd: Current Work Directory
    :param ctry: Country (ISO31661Alfa2Enum)
    :param exp_state: List of states in the country
    """
    os.chdir(cwd)
    countries_json, cities_json = load_files(ctry)
    assert isinstance(countries_json, list) and isinstance(cities_json, list)
    for city in cities_json:
        assert city["country_code"] == ctry.name
    assert exp_state == [state['name'] for state in countries_json]


# _______Order cities test___________

@pytest.mark.parametrize(
    'list_cities,list_dict,expected_list',
    [
        (['a', 'b', 'C'],
         [{'name': 'á', 'alternate_names': ['a', 'A', 'aaa'], 'more_info': ['info', 'more info'], 'population': 5},
          {'name': 'z', 'alternate_names': ['z', 'Z', 'zzz'], 'more_info': ['info', 'more info'], 'population': 5},
          {'name': 'C', 'alternate_names': ['c', 'CC'], 'more_info': ['info', 'more info'], 'population': 40}],
         ['C', 'á']
         ),
        (['a', 'b', 'C'],
         [{'name': 'á', 'alternate_names': ['A', 'aaa'], 'more_info': ['info', 'more info'], 'population': 5},
          {'name': 'z', 'alternate_names': ['z', 'Z', 'zzz'], 'more_info': ['info', 'more info'], 'population': 5},
          {'name': 'J', 'alternate_names': ['j', 'CC'], 'more_info': ['info', 'more info'], 'population': 40}],
         []
         ),
        ([],
         [{'name': 'á', 'alternate_names': ['A', 'aaa'], 'more_info': ['info', 'more info'], 'population': 5},
          {'name': 'z', 'alternate_names': ['z', 'Z', 'zzz'], 'more_info': ['info', 'more info'], 'population': 5},
          {'name': 'J', 'alternate_names': ['j', 'CC'], 'more_info': ['info', 'more info'], 'population': 40}],
         []
         ),
        (['j', 'k', 'l'],
         [],
         []
         ),
        (['l D.C.', 'J', 'X'],
         [{'name': 'L', 'alternate_names': ['l D.C.', 'l'], 'more_info': ['info', 'more info'], 'population': 5},
          {'name': 'z', 'alternate_names': ['z', 'Z', 'zzz'], 'more_info': ['info', 'more info'], 'population': 5},
          {'name': 'J', 'alternate_names': ['j', 'CC'], 'more_info': ['info', 'more info'], 'population': 40},
          {'name': 'X D.F.', 'alternate_names': ['x D.F.', 'x', 'X'], 'more_info': ['info', 'more info'],
           'population': 40}
          ],
         ['J', 'X D.F.', 'L']
         ),
        (['l D.C.', 'J', 'X'],
         [{'name': 'L', 'alternate_names': ['l D.C.', 'l'], 'more_info': ['info', 'more info'], 'population': 5},
          {'name': 'z', 'alternate_names': ['z', 'Z', 'zzz'], 'more_info': ['info', 'more info'], 'population': 5},
          {'name': 'X D.F.', 'alternate_names': ['x D.F.', 'x', 'X'], 'more_info': ['info', 'more info'],
           'population': 40},
          {'name': 'J', 'alternate_names': ['j', 'CC'], 'more_info': ['info', 'more info'], 'population': 40}
          ],
         ['X D.F.', 'J', 'L']
         )
    ]
)
def test_order_cities(list_cities, list_dict, expected_list):
    """
    Get a list of strings (cities) ordered by population
    :param list_cities: A list of strings that simulates a list of city names
    :param list_dict: A list of dictionaries that simulates a list of cities with demographic information
    :param expected_list: The list of strings (cities) ordered from largest to smallest population

    NOTES: If a string in the list 'list_cities' is not the value of the key 'name' nor is in the list 
    of the key 'alternate_names' then the string will not be considered in the final list.
    """
    assert order_cities(list_cities, list_dict) == expected_list


# ___________test NoSearchTermException__________
def test_no_search_term_exception():
    """
    Test NoSearchTermException: when there is no search term (Google Business Categories)
    """
    cls = GoogleMapsWebWrapper()
    cls.city = 'Bucaramanga'
    cls.country = ISO31661Alfa2Enum.CO
    args = (cls.city, None, cls.country, None)
    with pytest.raises(NoSearchTermException):
        cls.generate_search_url(None, *args)
        # assert str(excinfo.value) == 'The search_term can\'t be empty'


# ___________test NoLocationException__________
def test_no_location_exception():
    """
    Test NoLocationException: when there are no location arguments
    """
    cls = GoogleMapsWebWrapper()
    cls.city = 'Bucaramanga'
    cls.country = ISO31661Alfa2Enum.CO
    args = ()
    with pytest.raises(NoLocationException) as excinfo:
        cls.generate_search_url(GoogleBusinessCategory.ANDALUSIAN_RESTAURANT, *args)
    assert str(excinfo.value) == 'There are no location args. Use minimum 1'


# ________test merge_location_args_________
@pytest.mark.parametrize(
    "city,country,state,oa,expected",
    [
        ('Medellin', ISO31661Alfa2Enum.CO, 'Antioquia', [], ('Medellin', 'Antioquia', ISO31661Alfa2Enum.CO)),
        ('Dammam', ISO31661Alfa2Enum.SA, None, [], ('Dammam', ISO31661Alfa2Enum.SA)),
        ('Paris', ISO31661Alfa2Enum.FR, None, ['Bastille'], ('Paris', ISO31661Alfa2Enum.FR, 'Bastille'))
    ]
)
def test_merge_location_args(city, country, state, oa, expected):
    """
    Merge location arguments
    :param city: City
    :param country: Country (ISO31661Alfa2Enum)
    :param state: State
    :param oa: Other Arguments
    :param expected: Expected merge (tuple)
    """
    a = merge_location_args(LocationArgs(city=city, country=country, state=state, other_args=oa))
    assert a == expected


# ______test generate_search_url________
@pytest.mark.parametrize(
    'cty,ctry,ste,oa,Business_cat,expected',
    [('Bucaramanga', ISO31661Alfa2Enum.CO, None, [], GoogleBusinessCategory.VELODROME,
      'https://www.google.com/search?q=Velodrome+bucaramanga+colombia&rlst=f#rlfi=hd'),
     ('Paris', ISO31661Alfa2Enum.FR, None, ['Bastille'], GoogleBusinessCategory.ANDALUSIAN_RESTAURANT,
      'https://www.google.com/search?q=Andalusian+restaurant+paris+bastille+france&rlst=f#rlfi=hd'),
     ('Medellin', ISO31661Alfa2Enum.CO, 'Antioquia', ['Comuna 13'], GoogleBusinessCategory.COLOMBIAN_RESTAURANT,
      'https://www.google.com/search?q=Colombian+restaurant+medellin+antioquia+comuna+13+colombia&rlst=f#rlfi=hd')
     ]
)
def test_generate_search_url(cty, ctry, ste, oa, Business_cat, expected):
    """
    Generate urls from specific parameters
    :param cty: City
    :param ctry: Country (ISO31661Alfa2Enum)
    :param ste: State
    :param oa: Other Arguments
    :param Business_cat: the thing to search (Google Business Categories)
    :param expected: Expected url
    """
    cls = GoogleMapsWebWrapper()
    cls.city = cty
    cls.country = ctry
    args = merge_location_args(LocationArgs(city=cty, country=ctry, state=ste, other_args=oa))
    url = cls.generate_search_url(Business_cat, *args)
    assert str(url) == expected


# ________test scrape_maps_____________
@pytest.mark.parametrize(
    'file,cty,ctry,Business_cat,expected_name',
    [('velodrome.html', 'Bucaramanga', ISO31661Alfa2Enum.CO, GoogleBusinessCategory.VELODROME, 'Alfonso Florez Ortiz'),
     ('bodytech_cartagena.html','Cartagena', ISO31661Alfa2Enum.CO, GoogleBusinessCategory.GYM,'Bodytech Plazuela')
     ]
)
@patch('services.maps_scraper.maps_wrapper.httpx.Client.get')  # The route to mock
def test_scrape_maps(mock_client, file, cty, ctry, Business_cat, expected_name):
    """
    Test scrape_maps with local HTML files
    :param mock_client: Mock to avoid using third party services (httpx.client)
    :param file: local HTML file
    :param cty:  City
    :param ctry: Country (ISO31661Alfa2Enum)
    :param Business_cat: the thing to search (Google Business Categories)
    :param expected: Expected name of the first business in the result list
    """
    with open(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','files',file)), 'r') as f:
        test_site = f.read()
    mock_response = httpx.Response(200, content=test_site.encode(),
                                   request=httpx.Request("GET", "http://test.example.com")) # Emulate response
    mock_client.return_value = mock_response  # Define the emulated response as the return value of the mock
    cls = GoogleMapsWebWrapper()
    cls.city = cty
    cls.country = ctry
    cls.business_category = Business_cat
    cls.country_phone_code = f'+{str(country_code_for_region(cls.country.name))}'
    cls.scrape_maps('http://test.example.com')
    assert expected_name in cls.scraped_companies.companies_list[0].name


# _________test new_search______
client = TestClient(router)  # Fast API test client


@pytest.mark.parametrize(
    'cty,ste,ctry,Business_cat',
    [('Bucaramanga', '', ISO31661Alfa2Enum.CO, GoogleBusinessCategory.VELODROME),
     ('La Paz', '', ISO31661Alfa2Enum.BO, GoogleBusinessCategory.ANDALUSIAN_RESTAURANT),
     ('Dammam', '', ISO31661Alfa2Enum.SA, GoogleBusinessCategory.INTERNATIONAL_AIRPORT)
     ]
)
@pytest.mark.asyncio
@patch('routers.maps_scraper.maps_scraper.maps_bot')  # The route to mock
async def test_new_search(mock_maps_bot, cty, ste, ctry, Business_cat):
    """
    Test Fast API response for a single search (new_search)
    :param mock_maps_bot: Mock to avoid using third party services (scrape GoogleMaps)
    :param cty: City
    :param ste: State
    :param ctry: Country (ISO31661Alfa2Enum)
    :param Business_cat: the thing to search (Google Business Categories)
    """
    loc_args = LocationArgs(city=cty, state=ste, country=ctry)
    response = client.post(f'http://localhost:8000/new_search/{Business_cat.value}', json={"city": cty,
                                                                                                            "state": ste,
                                                                                                            "country": ctry.value,
                                                                                                            "other_args": []})
    assert response.status_code == 200
    assert response.json() == {'message': 'Maps scrapper started'}
    assert len(mock_maps_bot.mock_calls) == 1
    assert mock_maps_bot.mock_calls[0].args == (Business_cat, loc_args)


# _________country_search FastApi______
@pytest.mark.parametrize(
    'ctry',
    [ISO31661Alfa2Enum.CO,
     ISO31661Alfa2Enum.BO,
     ISO31661Alfa2Enum.SA,
     ISO31661Alfa2Enum.FR
     ]
)
@pytest.mark.asyncio
@patch('routers.maps_scraper.maps_scraper.search_by_country')
async def test_country_search(mock_search_by_country, ctry):
    """
    Test Fast API response for whole country search (country_search)
    :param mock_search_by_country: Mock to avoid using third party services (scrape GoogleMaps)
    :param ctry: Country (ISO31661Alfa2Enum)
    """
    response = client.get(f'http://localhost:8000/country_search/{ctry.value}')
    assert response.status_code == 200
    assert response.json() == {'message': f'Automatic business search in {ctry.value} started'}
    assert len(mock_search_by_country.mock_calls) == 1
    assert mock_search_by_country.mock_calls[0].args == (ctry,)


# ______search_by_country_____

# @pytest.mark.parametrize(
#     'test_info,expected',
#     [
#         (
#                 ([
#                      {'name': 'State A',
#                       'cities': [
#                           {'name': 'City1'},
#                           {'name': 'City2'},
#                           {'name': 'City3'},
#                           {'name': 'City4'},
#                           {'name': 'City5'},
#                           {'name': 'City6'}
#                       ]
#                       },
#                      {'name': 'State B',
#                       'cities': [
#                           {'name': 'CityA'},
#                           {'name': 'CityB'},
#                           {'name': 'CityC'},
#                           {'name': 'CityD'}
#                       ]
#                       }
#                  ],
#                  [{'name': 'City1', 'alternate_names': [], 'population': 5},
#                   {'name': 'City2', 'alternate_names': [], 'population': 4},
#                   {'name': 'City3', 'alternate_names': [], 'population': 3},
#                   {'name': 'City4', 'alternate_names': [], 'population': 2},
#                   {'name': 'City5', 'alternate_names': [], 'population': 1},
#                   {'name': 'City6', 'alternate_names': [], 'population': 0},
#                   {'name': 'CityA', 'alternate_names': [], 'population': 5},
#                   {'name': 'CityB', 'alternate_names': [], 'population': 4},
#                   {'name': 'CityC', 'alternate_names': [], 'population': 3},
#                   {'name': 'CityD', 'alternate_names': [], 'population': 2}
#                   ]),
#                 ['5 interesting cities found in State A',
#                  '4 interesting cities found in State B',
#                  'City1', 'City2', 'City3', 'City4', 'City5',
#                  'CityA', 'CityB', 'CityC', 'CityD'
#                  ]
#         )
#     ]
# )
# @patch('services.maps_bot.load_files')  # The route to mock
# @patch('services.maps_bot.maps_bot')  # The route to mock
# def test_search_by_country(mock_maps, mock_load, test_info, expected, capsys):
#     '''
#     Test the function to scrape business in a whole country (search_by_country)
#     :param mock_maps: Mock to avoid using third party services (scrape GoogleMaps)
#     :param mock_load: Mock to avoid loading information from local json files
#     :param test_info: Simulated countries and cities values
#     :param expected: Expected messages in console
#     :param capsys: Parameter to read what is displayed in the console
#     '''
#     mock_load.return_value = test_info
#     search_by_country(ISO31661Alfa2Enum.CO)
#     assert len(mock_load.mock_calls) == 1
#     captured = capsys.readouterr()  # read what is displayed in the console
#     for text in expected:
#         assert text in captured.out


# _______abbreviated_number_to_int______
@pytest.mark.parametrize(
    'input,output', [
        ('1\xa0K', 1000),
        ('1.5K', 1500),
        ('2.7M', 2700000),
        ('456', 456),
        ('2\xa0M', 2000000),
        ('1 K', 1000),
        ('50 M', 50000000),
        ('23.4\xa0K', 23400),
        ('5.3 K', 5300),
        ('34', 34),
        ('34.4 M', 34400000),
        ('24.55\xa0K', 24550)
    ]
)
def test_abbreviated_number_to_int(input, output):
    '''
    Test the function that converts an abbreviated number (i.e. 1.2K) to int (1200)
    :param input: Str with a number or abbreviated number
    :param output: corresponding to the abbreviated number
    '''
    assert abbreviated_number_to_int(input) == output


# _______delete_duplicates_from_list______
@pytest.mark.parametrize(
    'input,output', [
        ([{'name': 'bssnsA', 'ctry': 'ctryA', 'cty': 'ctyA', 'adress': 'addrsA', 'score': 5, 'num_op': 100},
          {'name': 'bssnsA', 'ctry': 'ctryA', 'cty': 'ctyA', 'adress': 'addrsA', 'score': 5, 'num_op': 100},
          {'name': 'bssnsB', 'ctry': 'ctryA', 'cty': 'ctyA', 'adress': 'addrsB', 'score': 4, 'num_op': 1200}],
         [{'name': 'bssnsA', 'ctry': 'ctryA', 'cty': 'ctyA', 'adress': 'addrsA', 'score': 5, 'num_op': 100},
          {'name': 'bssnsB', 'ctry': 'ctryA', 'cty': 'ctyA', 'adress': 'addrsB', 'score': 4, 'num_op': 1200}]),
        ([{'name': 'bssnsA', 'ctry': 'ctryA', 'cty': 'ctyA', 'adress': 'addrsA', 'score': 5, 'num_op': 100},
          {'name': 'bssnsA_', 'ctry': 'ctryA', 'cty': 'ctyA', 'adress': 'addrsA_', 'score': 5, 'num_op': 100},
          {'name': 'bssnsB', 'ctry': 'ctryA', 'cty': 'ctyA', 'adress': 'addrsB', 'score': 4, 'num_op': 1200}],
         [{'name': 'bssnsA', 'ctry': 'ctryA', 'cty': 'ctyA', 'adress': 'addrsA', 'score': 5, 'num_op': 100},
          {'name': 'bssnsA_', 'ctry': 'ctryA', 'cty': 'ctyA', 'adress': 'addrsA_', 'score': 5, 'num_op': 100},
          {'name': 'bssnsB', 'ctry': 'ctryA', 'cty': 'ctyA', 'adress': 'addrsB', 'score': 4, 'num_op': 1200}])

    ]
)
def test_delete_duplicates_from_list(input, output):
    """
    Test the function that deletes duplicated objects from a list.
    :param input: any list
    :param output: the list without duplicates objects
    """
    assert delete_duplicates_from_list(input) == output
