from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


class Timezone(BaseModel):
    zoneName: str
    gmtOffset: int
    gmtOffsetName: str
    abbreviation: str
    tzName: str


class Country(BaseModel):
    country_id: UUID
    country_active: bool
    country_created_at: datetime
    country_updated_at: datetime
    country_name: str
    country_country_id: str
    country_iso3: str
    country_iso2: str
    country_numeric_code: str
    country_phone_code: str
    country_capital: str
    country_currency: str
    country_currency_name: str
    country_currency_symbol: str
    country_tld: str
    country_native: str
    country_nationality: str
    country_timezones: List[Timezone]
    country_latitude: str
    country_longitude: str
    country_emoji: str
    country_emoji_u: str
    country_subregion_id: UUID


class State(BaseModel):
    state_id: UUID
    state_active: bool
    state_created_at: datetime
    state_updated_at: datetime
    state_name: str
    state_state_id: str
    state_latitude: str
    state_longitude: str
    state_country_id: UUID


class City(BaseModel):
    city_id: UUID
    city_active: bool
    city_created_at: datetime
    city_updated_at: datetime
    city_name: str
    city_city_id: str
    city_state_id: UUID


class CategoryValue(BaseModel):
    name: str
    value: str


class Category(BaseModel):
    category_id: UUID
    category_active: bool
    category_created_at: datetime
    category_updated_at: datetime
    category_name: str
    category_value: CategoryValue
    category_validation_type: Optional[str]
    category_group_definition: Optional[str]


class Campaign(BaseModel):
    campaign_id: UUID
    campaign_active: bool
    campaign_created_at: datetime
    campaign_updated_at: datetime
    campaign_name: str
    campaign_type: str
    campaign_status: str
    campaign_fields: str
    campaign_results: Optional[Any]
    campaign_duration: datetime
    campaign_organization_id: UUID
    campaign_city_id: UUID
    campaign_category_id: UUID
    campaign_bot_id: Optional[str]


class CampaignDetails(BaseModel):
    campaign: Campaign
    category: Category
    city: City
    state: State
    country: Country


class CreatedCampaign(BaseModel):
    categoryId: str
    cityId: str
    duration: datetime
    fields: str
    name: str
    organizationId: str
    status: str
    type: str
    active: bool
    updatedAt: datetime
    results: Optional[object]  # Assuming 'results' can be any type, including None
    id: str
    createdAt: datetime


class CampaignPayload(BaseModel):
    createdCampaign: CreatedCampaign
