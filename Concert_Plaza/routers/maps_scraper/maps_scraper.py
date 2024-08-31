from fastapi import APIRouter, Body, Path
from starlette.background import BackgroundTasks

from schemas.depends import ISO31661Alfa2Enum
from schemas.maps_scraper.google_business_category import GoogleBusinessCategory
from schemas.maps_scraper.location_args import LocationArgs
from services.maps_bot import maps_bot, search_by_country

router = APIRouter()


@router.post("/new_search/{search_term}", response_model=dict)
async def new_search(
        background_tasks: BackgroundTasks,
        search_term: GoogleBusinessCategory = Path(
            ..., description='Google Business Category'),
        campaign_id: str | None = None,
        location_args: LocationArgs = Body(
            ..., description='Arguments to describe location to search'),
) -> dict:
    background_tasks.add_task(maps_bot, search_term, location_args,campaign_id)
    return {'message': 'Maps scrapper started'}


@router.get("/country_search/{country}", response_model=dict)
async def country_search(
        background_tasks: BackgroundTasks,
        country: ISO31661Alfa2Enum = Path(..., description='Country'),
        campaign_id: str | None = None,
) -> dict:
    background_tasks.add_task(search_by_country, country, campaign_id)
    return {'message': f'Automatic business search in {country.value} started'}


@router.get("/health-check", )
async def health() -> dict:
    return {'status': 200, 'message': 'the service is working'}
