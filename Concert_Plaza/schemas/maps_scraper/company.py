from datetime import datetime

from pydantic import BaseModel, Field
#from pydantic_extra_types.phone_numbers import PhoneNumber

from schemas.depends import ISO31661Alfa2Enum, SocialMedia
from schemas.maps_scraper.google_business_category import GoogleBusinessCategory


class Company(BaseModel):
    name: str
    country: ISO31661Alfa2Enum | None = Field(None, example='USA')
    city: str
    date: datetime
    business_category: GoogleBusinessCategory
    score: float | None
    number_of_opinions: int
    address: str | None
    campaign_id: str | None
    phone_number: str | None
    website: str | None
    emails: list[str] | None = None
    social_media: SocialMedia | None = None


class Companies(BaseModel):
    companies_list: list[Company]
