import asyncio
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from translate import Translator
import requests
import random
from datetime import datetime, timedelta

from config import TOKEN1, NASA_API_KEY

bot = Bot(token=TOKEN1)
dp = Dispatcher(bot=bot)

def get_random_apod():
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    random_date = start_date + (end_date - start_date) * random.random()
    date_str = random_date.strftime('%Y-%m-%d')

    url = f'https://api.nasa.gov/planetary/apod?api_key={NASA_API_KEY}&date={date_str}'
    response = requests.get(url)
    return response.json()

@dp.message(Command('random_apod'))
async def random_apod(message: Message):
    apod = get_random_apod()
    photo_url = apod['url']
    title = apod['title']

    await message.answer_photo(photo=photo_url, caption=f'{title}')



async def main():
    await dp.start_polling(bot, skip_updates=True)

if __name__ == '__main__':
    asyncio.run(main())