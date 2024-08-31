import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
import threading
#from services.campaign.subscriber import handle_redis_subscription

from fastapi.middleware.cors import CORSMiddleware

from routers.routers import add_routers
from version import __version__

import constants as constants



@asynccontextmanager
async def lifespan(app: FastAPI):
    thread = threading.Thread(
        #target=handle_redis_subscription, args=("createdCampaign-{}",)
    )
    thread.start()
    yield


app = FastAPI(
    title=constants.OPEN_API_TITLE,
    description=constants.OPEN_API_DESCRIPTION,
    version=__version__,
    lifespan=lifespan
)

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins= settings.ORIGINS,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# Configure routes
add_routers(app)


@app.get(
    "/",
)
async def health() -> dict:
    return {"status": 200, "message": "the service is working"}





if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=4001)
