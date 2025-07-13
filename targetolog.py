from aiogram import types, Dispatcher, Bot, F
import asyncio
from config import bot_token
from aiogram.types import FSInputFile
from aiogram.filters import Command
from gpt_openai_api import get_texts
from llm import call_gpt, gpt
from llm import history

bot = Bot(token=bot_token)
dp = Dispatcher()


@dp.message(Command("parse"))
async def parse(message: types.Message):
    msg = await message.reply("Пожалуйста подождите!")
    res = get_texts()
    for i in res:
        await message.reply(f"{i}")
    await bot.delete_message(chat_id=message.chat.id, message_id=msg.message_id)
    r = call_gpt(res)
    with open("tz.txt", "w", encoding="utf-8") as f:
        f.write(r['content'])

    document = FSInputFile("tz.txt")
    await message.answer_document(document=document, caption="Ответ от gpt :)")
    # await message.answer(text=r['content'])


@dp.message(Command("ask"))
async def get_start(message: types.Message):
    t = message.text

    if t.startswith("/ask "):
        extracted_text = t[5:]
        m = await message.reply(f"U asked: {extracted_text}")

        competitor_creatives = get_texts()
        l = f"{extracted_text}\n\nНиже тексты конкурентов:\n\n"
        for i in competitor_creatives:
            l += f"Текст:\n{i}"
        # l = f"{extracted_text}\n\nНиже тексты конкурентов: {competitor_creatives}"
        # history.append({"role": "user", "content": l})
        r = gpt(l)

        with open("tz.txt", "w", encoding="utf-8") as f:
            f.write(r)
        abzacs = r.split("---")
        document = FSInputFile("tz.txt")
        # history.append({"role": "assistent", "content": r['content']})
        for i in abzacs:
            await message.answer(text=i)
        await message.answer_document(document=document, caption="Ответ от gpt :)")


        print(m.message_id)
    else:
        await message.reply("/ask <ваш запрос>!\n Пожалуйста следуйте инструкциям")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())