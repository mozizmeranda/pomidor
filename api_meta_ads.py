from environs import Env
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
import requests
from collections import defaultdict
from datetime import datetime
from database import db

env = Env()
env.read_env()

app_id = env.str("APP_ID")
app_secret = env.str("APP_SECRET")
access_token = env.str("ACCESS_TOKEN")
ad_account_id = 'act_1011840574303712'  # Sherzod Djalilov
# audience_id = 120230787401000283
facebook_id = 735875899606197
instagram_id = 17841442948535136

campaign_id_v1 = 120230933381480283
campaign_id_v2 = 120230950013850283

isso_id = 1011840574303712

adset_id = 120230950033290283

FacebookAdsApi.init(app_id, app_secret, access_token)

FacebookAdsApi.init(app_id, app_secret, access_token)
my_account = AdAccount(ad_account_id)


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


def get_interests(adset_id):
    url = f"https://graph.facebook.com/v23.0/{adset_id}"
    params = {
        "fields": "targeting,daily_budget",
        "access_token": access_token
    }
    response = requests.get(url, params=params)
    data = response.json()
    body = {}
    interests = ""
    try:
        flexible_spec = data["targeting"]["flexible_spec"]
        for spec in flexible_spec:
            if "interests" in spec:
                for interest in spec["interests"]:
                    interests += f"{interest['name']}, "
        body['interests'] = interests
        body['daily_budget'] = data['daily_budget']
    except KeyError:
        pass

    return body


# print(get_interests(120215617003820753))


def get_metrics_from_meta(campaign_id: int, date_since):
    timestamp = datetime.now().strftime("%Y-%m-%d")
    interests = ""
    url = (
        f"https://graph.facebook.com/v23.0/act_1011840574303712/insights"
        f"?level=adset"
        f"&fields=campaign_id,adset_id,campaign_name,adset_name,date_start,date_stop,"
        f"spend,impressions,clicks,ctr,cpm,actions"
        f"&access_token={access_token}"
        f"&filtering=[{{\"field\":\"campaign.id\",\"operator\":\"EQUAL\",\"value\":\"{campaign_id}\"}}]&"
        f"time_range[since]={date_since}&time_range[until]={timestamp}&time_increment=1&breakdowns="
    )
    # print(date_since, timestamp)

    response = requests.get(url)
    data = response.json()
    # print(data)
    for row in data["data"]:
        spend = float(row.get("spend", 0))
        impressions = int(row.get("impressions", 0))
        clicks = int(row.get("clicks", 0))

        leads = 0
        for action in row.get("actions", []):
            if action["action_type"] in ["lead", "onsite_conversion.lead_grouped"]:
                leads += int(action.get("value", 0))

        cr = round(leads / clicks, 4) if clicks > 0 else 0
        cpl = round(spend / leads, 4) if leads > 0 else 0
        ctr = round(clicks / impressions * 100, 4) if impressions > 0 else 0
        cpm = round(spend / impressions * 1000, 4) if impressions > 0 else 0

        timestamp = row['date_stop']
        params = (
            row["adset_id"],
            row['adset_name'],
            row["campaign_id"],
            timestamp,
            spend,
            impressions,
            clicks,
            leads,
            cr,
            cpl,
            ctr,
            cpm
        )
        # print(params)
        db.insert_ad_metrics(params=params)


# print((get_metrics(120215614681840753, "2025-08-01")))


def set_adset_status(adset_id, status):
    """
    status: 'ACTIVE' или 'PAUSED'
    """
    url = f"https://graph.facebook.com/v23.0/{adset_id}"
    params = {
        "status": status,
        "access_token": access_token
    }
    response = requests.post(url, data=params)
    return response.json()


def update_adset_budget(adset_id, daily_budget_usd):
    """
    daily_budget_usd — в долларах, конвертируем в центы (Facebook принимает в минимальных единицах валюты)
    """
    budget_in_cents = int(daily_budget_usd)
    url = f"https://graph.facebook.com/v23.0/{adset_id}"
    params = {
        "daily_budget": budget_in_cents,
        "access_token": access_token
    }
    response = requests.post(url, data=params)
    return response.json()


def get_adset_name_by_id(adset_id):
    url = f"https://graph.facebook.com/v23.0/{adset_id}"
    params = {
        "fields": "name,daily_budget",
        "access_token": access_token
    }
    resp = requests.get(url, params=params).json()
    return resp


# print(get_adset_name_by_id("120215616952620753"))


def get_metrics_from_db():
    metrics = db.get_metrics()

    # grouped[adset_id] = {"name": adset_name, "rows": [..]}
    grouped = defaultdict(lambda: {"name": "", "rows": []})
    for row in metrics:
        adset_id = row[1]
        adset_name = row[2]
        grouped[adset_id]["name"] = adset_name
        grouped[adset_id]["rows"].append(row)

    full_text = ""
    for adset_id, data in grouped.items():
        body = get_interests(int(adset_id))
        full_text += (f"### Adset ID: {adset_id} — {data['name']}.\n Интересы: {body['interests']}. "
                      f"Daily_budget: {body['daily_budget']} центов.\n\n")
        full_text += "| Date | Потрачено, $ | Impressions | Clicks | Leads | CR | CPL | CTR | CPM |\n"
        full_text += "| --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"

        # r: (id, adset_id, adset_name, campaign_id, timestamp, spend, impressions, clicks, leads, cr, cpl, ctr, cpm)
        for r in data["rows"]:
            full_text += (
                f"| {r[4]} | {r[5]} | {r[6]} | {r[7]} | {r[8]} | {r[9]} | {r[10]} | {r[11]} | {r[12]} |\n"
            )
        full_text += "\n\n"

    return full_text
