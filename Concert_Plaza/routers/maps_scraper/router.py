from fastapi import FastAPI, APIRouter

from .maps_scraper import router as maps_scraper_include_router


def include_router(app: FastAPI):
    api_router = APIRouter()
    api_router.include_router(maps_scraper_include_router, prefix='', tags=['Maps Scraper'])
    app.include_router(api_router, prefix='/maps-scraper')
