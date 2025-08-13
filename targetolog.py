from aiogram import types, Dispatcher, Bot
import asyncio
from config import bot_token
from aiogram.filters import Command
from api_meta_ads import get_metrics_from_db
from llm import gpt_v2
from apscheduler.schedulers.background import BackgroundScheduler
import requests


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


def async_send():
    requests.get(f"https://api.telegram.org/bot{bot_token}/sendMessage?"
                 f"chat_id=6287458105&text=Hello")
    # bot.send_message(6287458105, "Hello")


# def start_scheduler():
#     scheduler.add_job(lambda: asyncio.run(async_send()), 'interval', seconds=15)
#     scheduler.start()

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.reply("Привет, я AI таргетолог.")


@dp.message(Command("gpt"))
async def gpt_request(message: types.Message):
    t = message.text

    if t.startswith("/gpt "):
        extracted_text = t[5:]
        await message.reply(f"You asked: {extracted_text}")
        r = gpt_v2(extracted_text)
        paragraphs = r.split("---")

        for i in paragraphs:
            await message.answer(text=i)

    else:
        pass


@dp.message(Command("analyze"))
async def get_creatives(message: types.Message):
    if message.text.startswith("/analyze "):
        extracted_text = message.text[9:]
        full_text = f"{extracted_text}\n\n{get_metrics_from_db()}"
        r = gpt_v2(full_text)
        print(r)
        paragraphs = r.split("---")
        for i in paragraphs:
            await message.answer(text=i)


async def main():
    await dp.start_polling(bot)
    # start_scheduler()
    # scheduler.add_job(async_send, "interval", seconds=5)
    # scheduler.start()


if __name__ == "__main__":
    asyncio.run(main())
