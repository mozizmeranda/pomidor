import requests
from config import open_ai_token

# openai_api_key = open_ai_token

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {open_ai_token}"
}

prompt = ("Ты маркетолог, ниже я пришлю тексты, конкурентов, твоя цель проанализировать их и выдать боли, которые они решают"
          "благодаря этим креативам. Также по ним написать тз для моего креатива, основываясь на креативы конкурентов.")

history = [
    {"role": "system", "content": prompt},
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