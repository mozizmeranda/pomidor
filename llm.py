import requests
from config import open_ai_token
import json
from api_meta_ads import llm_create_campaign, llm_create_adset

# openai_api_key = open_ai_token

competitors = {
    "Гребенюк": "1",
    "Insan.uzb": "2",
    "alisher_avazov": "3"
}


headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {open_ai_token}"
}


prompt = ("Ты маркетолог, ниже я пришлю тексты, конкурентов, твоя цель проанализировать их и выдать боли, которые они решают "
          "благодаря этим креативам. Также по ним написать тз для моего креатива, основываясь на креативы конкурентов."
          " Благодаря функция create_campaign ты можешь создавать кампании в meta ads, тебе нужно попросить название и "
          "дневной бюджет. ")

p = ("Ты таргетолог, я могу тебя просить делать что-то. Ты можешь анализировать мои метрики. Также ты должен будешь мне "
     "создавать креативы и делать рутину таргетолога.\nБлагодаря функция create_campaign ты можешь создавать кампании в "
     "meta ads, тебе нужно попросить название и дневной бюджет(в центах, доставай в центах) для этого. Веди себя как специалист."
     "После создания кампании пришлю пользователю ID этой кампании.\nБлагодаря функции create_adset ты можешь создавать"
     "группы объявлений, в аргументы для этой функции достаточно принять название для группы объявлений и ID "
     "кампании и аудитории, дальше пришли"
     "ID созданной группы объявлений!")

history = [
    {"role": "system", "content": p},
]


def call_gpt(user_input):
    l = ""
    a = 1
    for i in user_input:
        l += f"Текст {a}:\n{i}"

    history.append({"role": "user", "content": l})
    body = {
        "model": "gpt-4.1",
        "messages": history,
    }
    url = "https://api.openai.com/v1/chat/completions"
    response = requests.post(url, headers=headers, json=body)
    return response.json()["choices"][0]["message"]


# tools = [
#     {
#         "type": "function",
#         "function":
#         {
#             "name": "create_campaign",
#             "description": "Создать сохранненую аудиторию для meta ads.",
#             "parameters": {
#                 "type": "object",
#                 "properties":
#                 {
#                     "name":
#                     {
#                         "type": "string",
#                         "description": "Название кампании в meta ads"
#                     },
#                     "daily_budget":
#                     {
#                         "type": "integer",
#                         "description": "Дневной бюджет для кампании в meta ads в центах, не переводи в доллары,"
#                                        " доставай в центах. Тебе отправят в центах, в центах и укажи!"
#                     },
#                 },
#                 "required": ["city", "daily_budget"]
#             }
#         }
#     }
# ]

tools = [
    {
        "type": "function",
        "function": {
            "name": "create_campaign",
            "description": "Создать кампанию для Meta Ads.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Название кампании в Meta Ads"
                    },
                    "daily_budget": {
                        "type": "integer",
                        "description": "Дневной бюджет кампании в центах (не переводить в доллары)"
                    }
                },
                "required": ["name", "daily_budget"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_adset",
            "description": "Создать ad set для кампании Meta Ads",
            "parameters": {
                "type": "object",
                "properties": {
                    "campaign_id": {
                        "type": "integer",
                        "description": "ID кампании Meta Ads"
                    },
                    "audience_id": {
                        "type": "integer",
                        "description": "ID сохранённой аудитории (Saved Audience)"
                    },
                    "name": {
                        "type": "string",
                        "description": "Название для группы объявлений"
                    }
                },
                "required": ["campaign_id", "audience_id", "name"]
            }
        }
    }
]

token = "7605174176:AAEdzUKDE0bYrMWv-NA7HQaw3T6hQZXLll0"
chat_id = -1002695927579

def gpt(text):
    history.append({"role": "user", "content": text})
    body = {
        "model": "gpt-4.1",
        "messages": history,
    }
    url = "https://api.openai.com/v1/chat/completions"
    response = requests.post(url, headers=headers, json=body)
    answer = response.json()["choices"][0]["message"]['content']
    history.append({"role": "assistant", "content": answer})
    return str(answer)


# def gpt_v2(text):
#     history.append({"role": "user", "content": text})
#     body = {
#         "model": "gpt-4.1",
#         "messages": history,
#         "tools": tools,
#         "tool_choice": "auto"  # GPT сам вызовет нужную функцию, если распознает
#     }
#     url = "https://api.openai.com/v1/chat/completions"
#     response = requests.post(url, headers=headers, json=body)
#     data = response.json()
#
#     message = data["choices"][0]["message"]
#
#     if "tool_calls" in message:
#         for tool_call in message["tool_calls"]:
#             if tool_call["function"]["name"] == "create_campaign":
#                 args = json.loads(tool_call["function"]["arguments"])
#                 print(f"Name: {args['name']} and budget: {args['daily_budget']}")
#                 d = llm_create_campaign(
#                     name=args["name"],
#                     daily_budget=args["daily_budget"]
#                 )
#                 requests.get(f"https://api.telegram.org/bot7605174176:AAEdzUKDE0bYrMWv-NA7HQaw3T6hQZXLll0/sendMessage?"
#                              f"chat_id=-1002695927579&text={d}")
#                 # print(d)
#
#                 # Возвращаем ответ с результатом
#                 history.append({
#                     "role": "function",
#                     "name": tool_call["function"]["name"],
#                     "content": f"Создана кампания с именем {args['name']} и дневная бюджетом {args['daily_budget']}"
#                                f"данные про кампанию: {d}"
#                 })
#
#                 # Перезапрос к GPT с результатом
#                 followup_body = {
#                     "model": "gpt-4.1",
#                     "messages": history
#                 }
#                 followup_response = requests.post(url, headers=headers, json=followup_body)
#                 return followup_response.json()["choices"][0]["message"]["content"]
#
#     # Обычный ответ (если без tools)
#     history.append({"role": "assistant", "content": message["content"]})
#     return message["content"]

def gpt_v2(text):
    history.append({"role": "user", "content": text})
    body = {
        "model": "gpt-4.1",
        "messages": history,
        "tools": tools,
        "tool_choice": "auto"
    }
    url = "https://api.openai.com/v1/chat/completions"
    response = requests.post(url, headers=headers, json=body)
    data = response.json()

    message = data["choices"][0]["message"]

    if "tool_calls" in message:
        for tool_call in message["tool_calls"]:
            function_name = tool_call["function"]["name"]
            args = json.loads(tool_call["function"]["arguments"])

            if function_name == "create_campaign":
                print(f"Name: {args['name']} and budget: {args['daily_budget']}")
                d = llm_create_campaign(
                    name=args["name"],
                    daily_budget=args["daily_budget"]
                )
                requests.get(f"https://api.telegram.org/bot{token}/sendMessage?"
                             f"chat_id={chat_id}&text={d}")
                history.append({
                    "role": "function",
                    "name": function_name,
                    "content": f"Создана кампания: {args['name']}, бюджет: {args['daily_budget']}\nОтвет: {d}"
                })

            elif function_name == "create_adset":
                print(f"Creating ad set with campaign_id: {args['campaign_id']}, audience_id: {args['audience_id']}")
                result = llm_create_adset(
                    name=args['name'],
                    campaign_id=args["campaign_id"],
                    audience_id=args["audience_id"]
                )
                requests.get(f"https://api.telegram.org/bot{token}/sendMessage?"
                             f"chat_id={chat_id}&text={result}")

                history.append({
                    "role": "function",
                    "name": function_name,
                    "content": f"Создан ad set для кампании {args['campaign_id']} с аудиторией {args['audience_id']}\nОтвет: {result}"
                })

        # После выполнения функции – делаем follow-up запрос
        followup_body = {
            "model": "gpt-4.1",
            "messages": history
        }
        followup_response = requests.post(url, headers=headers, json=followup_body)
        return followup_response.json()["choices"][0]["message"]["content"]

    # Ответ без вызова функции
    history.append({"role": "assistant", "content": message["content"]})
    return message["content"]

