import re

import httpx
from bs4 import BeautifulSoup


def scrape_websites(self):
    """
    Search for relevant information in attached websites in companies list attribute
    """
    for company in self.scraped_companies.companies_list:
        if company.website:
            try:
                response = self.client.get(str(company.website), headers=self.headers)
            except httpx.HTTPError:
                company.website = None
                continue
            soup = BeautifulSoup(response, features='lxml')
            email_list = re.findall(r"[\w.-]+@\w+.com", soup.text)
            if email_list:
                company.emails = email_list[-1]
