from fastapi import FastAPI

from .maps_scraper.router import include_router as maps_scraper_include_router


def add_routers(app: FastAPI) -> None:
    maps_scraper_include_router(app)
