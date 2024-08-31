import httpx
from fake_http_header import FakeHttpHeader

from schemas.maps_scraper.company import Companies


class WebWrapper:
    def __init__(self, timeout: float = 10.0, proxies: dict | None = None):
        self.client: httpx.Client = httpx.Client(timeout=timeout, proxies=proxies)
        self.headers = self._generate_new_headers()
        self.scraped_companies: Companies = Companies(companies_list=list())

    def set_companies(self, companies: Companies):
        self.scraped_companies = companies

    def close_client(self):
        """
        Close the class httpx client
        """
        self.client.close()

    @staticmethod
    def _generate_new_headers() -> dict:
        """
        FakeHttpHeader has error when in COUNTRY_TOP_LEVEL_DOMAINS random choice
        chooses eu, so retry in that case until it works selecting other value
        """
        while True:
            try:
                return FakeHttpHeader().as_header_dict()
            except KeyError:
                pass
