import re

import httpx
from bs4 import BeautifulSoup

from exceptions import FailedToGetURL
from schemas.depends import SocialMedia, SocialMediaEnum
from schemas.maps_scraper.company import Companies
from services.depends import WebWrapper


class LandingWebWrapper(WebWrapper):
    """Landing pages Web Wrapper"""

    def __init__(self, companies: Companies, timeout: float = 10.0, proxies: dict | None = None):
        """
        Create the class, define the typing and set default values for all attributes
        :param timeout: Set the timeout time for all the requests. Default 10s
        """
        super().__init__(timeout=timeout, proxies=proxies)
        self.set_companies(companies)

    def scrape_landing_pages(self):
        for company in self.scraped_companies.companies_list:
            if company.website:
                try:
                    response = self.client.get(str(company.website), headers=self.headers, follow_redirects=True)
                except httpx.HTTPError as e:
                    #print('\n\nERROR GETTING URL. CHECK IP BLOCK\n\n\n')
                    #raise FailedToGetURL(e)
                    continue
                soup = BeautifulSoup(response.content, features='lxml')
                body = soup.find('body')
                if body:
                    company.emails = self.scrape_emails(body)
                    company.social_media = self.scrape_social_media_urls(body)

    @staticmethod
    def scrape_emails(bs_to_scrape: BeautifulSoup) -> list[str]:
        return list(set(re.findall(r'\w+@\w+\.\w+', bs_to_scrape.get_text(separator=' ', strip=True))))

    @staticmethod
    def scrape_social_media_urls(bs_to_scrape: BeautifulSoup) -> SocialMedia:
        list_of_links = [link['href'] for link in bs_to_scrape.find_all('a') if link.has_attr('href')]
        base_args = {
            SocialMediaEnum.FACEBOOK: [],
            SocialMediaEnum.INSTAGRAM: [],
            SocialMediaEnum.LINKEDIN: [],
            SocialMediaEnum.TWITTER: [],
            SocialMediaEnum.TIKTOK: [],
            SocialMediaEnum.BNI: []
        }
        for link in list_of_links:
            if SocialMediaEnum.FACEBOOK in link:
                base_args[SocialMediaEnum.FACEBOOK].append(link)
            if SocialMediaEnum.INSTAGRAM in link:
                base_args[SocialMediaEnum.INSTAGRAM].append(link)
            if SocialMediaEnum.LINKEDIN in link:
                base_args[SocialMediaEnum.LINKEDIN].append(link)
            if SocialMediaEnum.TWITTER in link:
                base_args[SocialMediaEnum.TWITTER].append(link)
            if SocialMediaEnum.TIKTOK in link:
                base_args[SocialMediaEnum.TIKTOK].append(link)
            if SocialMediaEnum.BNI in link:
                base_args[SocialMediaEnum.BNI].append(link)
        base_args[SocialMediaEnum.FACEBOOK] = list(set(base_args[SocialMediaEnum.FACEBOOK]))
        base_args[SocialMediaEnum.INSTAGRAM] = list(set(base_args[SocialMediaEnum.INSTAGRAM]))
        base_args[SocialMediaEnum.LINKEDIN] = list(set(base_args[SocialMediaEnum.LINKEDIN]))
        base_args[SocialMediaEnum.TWITTER] = list(set(base_args[SocialMediaEnum.TWITTER]))
        base_args[SocialMediaEnum.TIKTOK] = list(set(base_args[SocialMediaEnum.TIKTOK]))
        base_args[SocialMediaEnum.BNI] = list(set(base_args[SocialMediaEnum.BNI]))
        return SocialMedia(**base_args)
