from aiogram import types, Dispatcher, Bot
import asyncio
from aiogram.types import FSInputFile, BotCommand
from config import bot_token
from aiogram.filters import Command
from api_meta_ads import get_metrics_from_db
from apscheduler.triggers.cron import CronTrigger
import re
from llm import gpt_v2
from api_meta_ads import save_as_mobile_html
from apscheduler.schedulers.background import BackgroundScheduler
import requests
from database import *


bot = Bot(token=bot_token)
dp = Dispatcher()
scheduler = BackgroundScheduler()

# @dp.message(Command("parse"))
# async def parse(message: types.Message):
#     msg = await message.reply("Пожалуйста подождите!")
#     res = get_texts()
#     for i in res:
#         await message.reply(f"{i}")
#     await bot.delete_message(chat_id=message.chat.id, message_id=msg.message_id)
#     r = call_gpt(res)
#     with open("tz.txt", "w", encoding="utf-8") as f:
#         f.write(r['content'])
#
#     document = FSInputFile("tz.txt")
#     await message.answer_document(document=document, caption="Ответ от gpt :)")
#     # await message.answer(text=r['content'])

requests.get(f"https://api.telegram.org/bot7080784217:AAGHD7Ne0qp7IWC8b4xQu7yhfxdAKxw2uus/sendMessage?"
             f"chat_id=6287458105&text=1")


@dp.message(Command("start"))
async def start(message: types.Message):
    await message.reply("Привет, я AI таргетолог.")


async def set_commands():
    commands = [
        BotCommand(command="start", description="Запуск бота"),
        BotCommand(command="campaigns", description="Чтобы получить все доступные кампании."),
        BotCommand(command="gpt", description="Запрос к GPT"),
        BotCommand(command="analyze", description="Анализ кампании"),
    ]
    await bot.set_my_commands(commands)


def format_for_telegram(text):
    """Форматирует текст для лучшего отображения в Telegram"""

    # Заменяем заголовки на жирный текст
    text = re.sub(r'##\s*(.*)', r'*\1*', text)  # ## Заголовок -> *Заголовок*
    text = re.sub(r'#\s*(.*)', r'**\1**', text)  # # Заголовок -> **Заголовок**

    # Заменяем списки на эмодзи
    text = re.sub(r'^\d+\.\s*', '🔸 ', text, flags=re.MULTILINE)
    text = re.sub(r'^\*\s*', '• ', text, flags=re.MULTILINE)
    text = re.sub(r'^-\s*', '• ', text, flags=re.MULTILINE)

    # Добавляем разделители
    # text = re.sub(r'\n\n', '\n━━━━━━━━━━━━━━━\n', text)

    return text


@dp.message(Command("gpt"))
async def gpt_request(message: types.Message):
    t = message.text

    if t.startswith("/gpt "):
        extracted_text = t[5:]
        await message.reply(f"You asked: {extracted_text}")
        r = gpt_v2(extracted_text)
        paragraphs = r.split("---")

        for i in paragraphs:
            await message.answer(text=format_for_telegram(i))

    else:
        pass


@dp.message(Command("analyze"))
async def get_creatives(message: types.Message):
    parts = message.text.strip().split(maxsplit=2)
    if len(parts) < 2:
        await message.reply("❗Формат: /analyze CAMPAIGN_ID \n\n[ваш текст]")
        return

    campaign_id = parts[1]
    extracted_text = parts[2] if len(parts) > 2 else ""

    metrics = get_metrics_from_db(campaign_id)
    full_text = f"{extracted_text}\n\n{metrics}"
    filename = save_as_mobile_html(metrics, 123)
    doc = FSInputFile(filename, "adset_report_123_mobile.html")
    await bot.send_document(
        chat_id=message.from_user.id,
        document=doc,
        caption=f"📊 Отчет"
    )
    r = gpt_v2(full_text)
    paragraphs = r.split("---")
    for i in paragraphs:
        await message.answer(text=i.replace("#", ""), parse_mode="MarkdownV2")


@dp.message(Command("text"))
async def get_creatives(message: types.Message):
    parts = message.text.strip().split(maxsplit=2)
    if len(parts) < 2:
        await message.reply("❗ Формат: /analyze CAMPAIGN_ID [ваш текст]")
        return

    campaign_id = parts[1]
    user_text = parts[2] if len(parts) > 2 else ""
    await message.reply(f"{campaign_id} -- {user_text}")


@dp.message(Command("campaigns"))
async def send_campaigns(message: types.Message):
    campaigns = db.get_campaigns()
    ans = ""
    ids = []
    for i in campaigns:
        if i[0] not in ids:
            ans += f"Name = {i[1]} -- ID = <code>{i[0]}</code>\n\n"
            ids.append(i[0])

    await message.reply(ans, parse_mode="HTML")


async def main():
    await set_commands()
    await dp.start_polling(bot)
    # start_scheduler()

    # start_scheduler()
    # scheduler.add_job(async_send, "interval", seconds=5)
    # scheduler.start()


if __name__ == "__main__":
    asyncio.run(main())
