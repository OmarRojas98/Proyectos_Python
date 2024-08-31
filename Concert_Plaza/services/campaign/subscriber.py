
import json
import redis

from config.settings import settings
from services.maps_bot import maps_bot
from models.campaign import CampaignPayload
from services.campaign.campaign import get_campaign, update_campaign

from schemas.maps_scraper.location_args import LocationArgs
from schemas.maps_scraper.google_business_category import GoogleBusinessCategory


#redis_client = redis.StrictRedis(host=settings.REDIS_HOST, port=6379, db=0, ssl=True)


# def handle_redis_subscription(channel_name: str):
#     pubsub = redis_client.pubsub()
#     pubsub.subscribe(channel_name)
#     for message in pubsub.listen():
#         if message["type"] == "message":
#             try:
#                 payload = CampaignPayload(**json.loads(message["data"].decode("utf-8")))
#                 print(f"Payload: {payload}")
#                 campaign = get_campaign(payload.createdCampaign.id)
#                 print(f"Campaign: {campaign}")

#                 if not campaign:
#                     print(f"Error getting campaign")
#                     return
#                 maps_bot(campaign_id=payload.createdCampaign.id, location_args=LocationArgs(city=campaign.city.city_name, state=campaign.state.state_name,country=campaign.country.country_name), business_category=GoogleBusinessCategory(campaign.category.category_name))
#                 update_campaign(campaign_id=payload.createdCampaign.id,)
#             except Exception as e:
#                 print(f"Error updating campaign {e}")