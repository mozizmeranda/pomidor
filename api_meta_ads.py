from environs import Env
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.adset import AdSet


env = Env()
env.read_env()

app_id = env.str("APP_ID")
app_secret = env.str("APP_SECRET")
access_token = env.str("ACCESS_TOKEN")
ad_account_id = 'act_1256548179458558'
# audience_id = 120230787401000283
facebook_id = 735875899606197
instagram_id = 17841442948535136

campaign_id_v1 = 120230933381480283
campaign_id_v2 = 120230950013850283

adset_id = 120230950033290283

FacebookAdsApi.init(app_id, app_secret, access_token)

FacebookAdsApi.init(app_id, app_secret, access_token)
my_account = AdAccount(ad_account_id)


# campaign = my_account.create_campaign(
#     params={
#         'name': 'Test Campaign from API',
#         'objective': 'OUTCOME_LEADS',  # или REACH, TRAFFIC, CONVERSIONS и т.д.
#         'status': 'PAUSED',  # 'ACTIVE' чтобы сразу запустить
#         'daily_budget': 200,
#         'special_ad_categories': []  # [] если не финанс/жильё/политика
#     }
# )
#
# print(campaign)


def llm_create_campaign(name: str, daily_budget):
    try:
        campaign = my_account.create_campaign(
            params={
                'name': name,
                'objective': 'OUTCOME_ENGAGEMENT',  # или REACH, TRAFFIC, CONVERSIONS и т.д.
                'status': 'PAUSED',  # 'ACTIVE' чтобы сразу запустить
                'daily_budget': int(daily_budget),
                'special_ad_categories': []  # [] если не финанс/жильё/политика
            }
        )

        print(campaign)
        return campaign
    except Exception as e:
        print(e)


# l = {
#     'name': 'Instagram Messages AdSet',
#     'campaign_id': 120230977110880283,
#
#     # Место получения конверсий: Instagram
#     'destination_type': 'INSTAGRAM_DIRECT',
#
#     # Цель по результативности: "максимальное количество лидов"
#     'optimization_goal': 'CONVERSATIONS',
#
#     'billing_event': 'IMPRESSIONS',
#     'bid_strategy': 'LOWEST_COST_WITHOUT_CAP',
#     'bid_amount': 100,
#
#     # Promoted object для messaging
#     'promoted_object': {
#         'page_id': facebook_id
#     },
#
#     # Таргетинг
#     'targeting': {
#         'geo_locations': {'countries': ['UZ']},  # Обязательно!
#         'publisher_platforms': ['instagram'],  # Только Instagram
#         'instagram_positions': ['stream'],  # Лента профиля Instagram
#     },
#
#     # ID вашей аудитории
#     'targeting_audience_id': 120230787401000283,
#
#     'status': 'PAUSED'
# }


def llm_create_adset(name: str, campaign_id: int, audience_id: int):
    try:
        l = {
            'name': name,
            'campaign_id': campaign_id,

            # Место получения конверсий: Instagram
            'destination_type': 'INSTAGRAM_DIRECT',

            # Цель по результативности: "максимальное количество лидов"
            'optimization_goal': 'CONVERSATIONS',

            'billing_event': 'IMPRESSIONS',
            'bid_strategy': 'LOWEST_COST_WITHOUT_CAP',
            'bid_amount': 100,

            # Promoted object для messaging
            'promoted_object': {
                'page_id': facebook_id
            },

            # Таргетинг
            'targeting': {
                'geo_locations': {'countries': ['UZ']},  # Обязательно!
                'publisher_platforms': ['instagram'],  # Только Instagram
                'instagram_positions': ['stream'],  # Лента профиля Instagram
            },

            # ID вашей аудитории
            'targeting_audience_id': audience_id,

            'status': 'PAUSED'
        }

        set = my_account.create_ad_set(params=l)
        # print(set)
        return set

    except Exception as e:
        print(e)

# print(llm_create_campaign("TEST v2", 200))

# print(llm_create_adset())



