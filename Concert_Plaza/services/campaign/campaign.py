import psycopg

from models.campaign import Campaign, CampaignDetails, Category, City, Country, State, Timezone
from config.settings import settings

# Configuración de la conexión a la base de datos



def get_campaign(campaign_id: str):
    try:
        conn = psycopg.connect(
            dbname=settings.DB_DATABASE,
            user=settings.DB_USERNAME,
            password=settings.DB_PASSWORD,
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            sslmode='require'  
        )
        with conn.cursor() as cursor:
            # Definir la consulta parametrizada
            query = """
            SELECT
                "Campaign"."id" AS "Campaign_id",
                "Campaign"."active" AS "Campaign_active",
                "Campaign"."created_at" AS "Campaign_created_at",
                "Campaign"."updated_at" AS "Campaign_updated_at",
                "Campaign"."name" AS "Campaign_name",
                "Campaign"."type" AS "Campaign_type",
                "Campaign"."status" AS "Campaign_status",
                "Campaign"."fields" AS "Campaign_fields",
                "Campaign"."results" AS "Campaign_results",
                "Campaign"."duration" AS "Campaign_duration",
                "Campaign"."organization_id" AS "Campaign_organization_id",
                "Campaign"."city_id" AS "Campaign_city_id",
                "Campaign"."category_id" AS "Campaign_category_id",
                "Campaign"."bot_id" AS "Campaign_bot_id",
                "category"."id" AS "category_id",
                "category"."active" AS "category_active",
                "category"."created_at" AS "category_created_at",
                "category"."updated_at" AS "category_updated_at",
                "category"."name" AS "category_name",
                "category"."value" AS "category_value",
                "category"."validation_type" AS "category_validation_type",
                "category"."group_definition" AS "category_group_definition",
                "city"."id" AS "city_id",
                "city"."active" AS "city_active",
                "city"."created_at" AS "city_created_at",
                "city"."updated_at" AS "city_updated_at",
                "city"."name" AS "city_name",
                "city"."city_id" AS "city_city_id",
                "city"."state_id" AS "city_state_id",
                "state"."id" AS "state_id",
                "state"."active" AS "state_active",
                "state"."created_at" AS "state_created_at",
                "state"."updated_at" AS "state_updated_at",
                "state"."name" AS "state_name",
                "state"."state_id" AS "state_state_id",
                "state"."latitude" AS "state_latitude",
                "state"."longitude" AS "state_longitude",
                "state"."country_id" AS "state_country_id",
                "country"."id" AS "country_id",
                "country"."active" AS "country_active",
                "country"."created_at" AS "country_created_at",
                "country"."updated_at" AS "country_updated_at",
                "country"."name" AS "country_name",
                "country"."country_id" AS "country_country_id",
                "country"."iso3" AS "country_iso3",
                "country"."iso2" AS "country_iso2",
                "country"."numeric_code" AS "country_numeric_code",
                "country"."phone_code" AS "country_phone_code",
                "country"."capital" AS "country_capital",
                "country"."currency" AS "country_currency",
                "country"."currency_name" AS "country_currency_name",
                "country"."currency_symbol" AS "country_currency_symbol",
                "country"."tld" AS "country_tld",
                "country"."native" AS "country_native",
                "country"."nationality" AS "country_nationality",
                "country"."timezones" AS "country_timezones",
                "country"."latitude" AS "country_latitude",
                "country"."longitude" AS "country_longitude",
                "country"."emoji" AS "country_emoji",
                "country"."emoji_u" AS "country_emoji_u",
                "country"."subregion_id" AS "country_subregion_id"
            FROM "campaign" "Campaign"
            LEFT JOIN "definition" "category" ON "Campaign"."category_id" = "category"."id"
            LEFT JOIN "city" "city" ON "Campaign"."city_id" = "city"."id"
            LEFT JOIN "state" "state" ON "city"."state_id" = "state"."id"
            LEFT JOIN "country" "country" ON "state"."country_id" = "country"."id"
            WHERE "Campaign"."id" = %s
            """
            # Reemplaza con el nombre de la tabla que deseas consultar
            cursor.execute(
                query, (campaign_id,))

            # Obtener los resultados
            rows = cursor.fetchall()
            data = rows[0]
            print(f"data {data}")
            campaign_details = CampaignDetails(
            campaign=Campaign(
                campaign_id=data[0],
                campaign_active=data[1],
                campaign_created_at=data[2],
                campaign_updated_at=data[3],
                campaign_name=data[4],
                campaign_type=data[5],
                campaign_state=data[6],
                campaign_status=data[6],
                campaign_fields=data[7],
                campaign_results=data[8],
                campaign_duration=data[9],
                campaign_organization_id=data[10],
                campaign_city_id=data[11],
                campaign_category_id=data[12],
                campaign_bot_id=data[13],
            ),
            category=Category(
                category_id=data[14],
                category_active=data[15],
                category_created_at=data[16],
                category_updated_at=data[17],
                category_name=data[18],
                category_value=data[19],
                category_validation_type=data[20],
                category_group_definition=data[21],
            ),
            city=City(
                city_id=data[22],
                city_active=data[23],
                city_created_at=data[24],
                city_updated_at=data[25],
                city_name=data[26],
                city_city_id=data[27],
                city_state_id=data[28],
            ),
            state=State(
                state_id=data[29],
                state_active=data[30],
                state_created_at=data[31],
                state_updated_at=data[32],
                state_name=data[33],
                state_state_id=data[34],
                state_latitude=data[35],
                state_longitude=data[36],
                state_country_id=data[37],
            ),
            country=Country(
                country_id=data[38],
                country_active=data[39],
                country_created_at=data[40],
                country_updated_at=data[41],
                country_name=data[42],
                country_country_id=data[43],
                country_iso3=data[44],
                country_iso2=data[45],
                country_numeric_code=data[46],
                country_phone_code=data[47],
                country_capital=data[48],
                country_currency=data[49],
                country_currency_name=data[50],
                country_currency_symbol=data[51],
                country_tld=data[52],
                country_native=data[53],
                country_nationality=data[54],
                country_timezones=[Timezone(**tz) for tz in data[55]],
                country_latitude=data[56],
                country_longitude=data[57],
                country_emoji=data[58],
                country_emoji_u=data[59],
                country_subregion_id=data[60],
            )
            )
            return campaign_details
    except Exception as e:
        print(f"Error: {e}")

    finally:
        # Cerrar la conexión a la base de datos
        conn.close()


def update_campaign(campaign_id: str):
    try:
        conn = psycopg.connect(
            dbname=settings.DB_DATABASE,
            user=settings.DB_USERNAME,
            password=settings.DB_PASSWORD,
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            sslmode='require'
        )
        with conn.cursor() as cursor:
            new_status = "COMPLETED"
            query = """
                UPDATE campaign
                SET status = %s, updated_at = NOW()
                WHERE id = %s
            """
           
            cursor.execute(
                query, (new_status, campaign_id,))
            conn.commit()
            print(f"Campaign {campaign_id} status updated to {new_status}")


          
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()


    finally:
        # Cerrar la conexión a la base de datos
        conn.close()