import re
from urllib.parse import urlparse

from schemas.maps_scraper.location_args import LocationArgs


def valid_http_url(url: str | None):
    """
    validates the website for every company. If not valid then company. Website is set to None
    :return:
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


def delete_duplicates_from_list(list_: list) -> list:
    """
    Delete duplicated objects from a list. To be duplicated all attributes of two or more objects must be the same
    :param list_: any list
    :return: the list without duplicates objects
    """
    return [i for n, i in enumerate(list_) if i not in list_[n + 1:]]


def abbreviated_number_to_int(abbreviated_number: str | None) -> int:
    """
    Converts an abbreviated or normal number to normal number. Ex: 1.2K to 1200 or 1000 to 1000
    :param abbreviated_number: Str with a number or abbreviated number
    :return: int corresponding to the abbreviated number
    """
    if not abbreviated_number:
        return 0
    try:
        return int(abbreviated_number)
    except ValueError:
        abbreviated_number = abbreviated_number.casefold().replace(u'\xa0', '').replace(' ', '')
        try:
            if 'k' in abbreviated_number:
                return int(float(re.search(
                    r'\d+\.?\d*', abbreviated_number).group(0).replace(',', '.')) * 1000)
            elif 'm' in abbreviated_number:
                return int(float(re.search(
                    r'\d+\.?\d*', abbreviated_number).group(0).replace(',', '.')) * 1000000)
            else:
                raise ValueError
        except ValueError:
            raise ValueError


def merge_location_args(location_args: LocationArgs) -> tuple:
    """
    transforms LocationArgs object into tuple of strings
    :param location_args: valid object of type LocationArgs
    :return: tuple of strings contained in location_args
    """
    args = []
    args.append(location_args.city) if location_args.city else None
    args.append(location_args.state) if location_args.state else None
    args.append(location_args.country) if location_args.country else None
    args.extend(location_args.other_args) if location_args.other_args else None
    return tuple(args)
