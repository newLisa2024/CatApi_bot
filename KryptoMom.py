import asyncio
import json
import time
import websockets
from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
import logging

from config import TOKEN2

# Настройка логирования
logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN2)
dp = Dispatcher()
router = Router()

# Обработчик сообщений от WebSocket
ticker_data_queue = asyncio.Queue()

async def connect_to_gateio():
    uri = "wss://api.gateio.ws/ws/v4/"

    async with websockets.connect(uri) as websocket:
        # Подписка на канал тикеров
        subscribe_message = {
            "time": int(time.time()),
            "channel": "spot.tickers",
            "event": "subscribe",
            "payload": ["BTC_USDT"]
        }
        await websocket.send(json.dumps(subscribe_message))

        while True:
            response = await websocket.recv()
            data = json.loads(response)
            logging.info(f"Received data: {data}")
            if data['event'] == 'update':
                await ticker_data_queue.put(data['result'])

async def get_ticker_data():
    return await ticker_data_queue.get()

@router.message(CommandStart())
async def start(message: Message):
    logging.info(f"Received /start command from {message.from_user.id}")
    await message.answer("Привет! Напиши /ticker, чтобы увидеть текущую информацию о BTC/USDT на Gate.io.")

@router.message(Command(commands="ticker"))
async def send_ticker(message: Message):
    logging.info(f"Received /ticker command from {message.from_user.id}")
    ticker_data = await get_ticker_data()
    if ticker_data:
        currency_pair = ticker_data.get('currency_pair', 'N/A')
        last_price = ticker_data.get('last', 'N/A')
        lowest_ask = ticker_data.get('lowest_ask', 'N/A')
        highest_bid = ticker_data.get('highest_bid', 'N/A')
        change_percentage = ticker_data.get('change_percentage', 'N/A')
        base_volume = ticker_data.get('base_volume', 'N/A')
        quote_volume = ticker_data.get('quote_volume', 'N/A')
        high_24h = ticker_data.get('high_24h', 'N/A')
        low_24h = ticker_data.get('low_24h', 'N/A')

        ticker_message = (
            f"Пара: {currency_pair}\n"
            f"Последняя цена: {last_price}\n"
            f"Лучшая цена спроса: {lowest_ask}\n"
            f"Лучшая цена предложения: {highest_bid}\n"
            f"Процент изменения: {change_percentage}%\n"
            f"Объем базовой валюты: {base_volume}\n"
            f"Объем котируемой валюты: {quote_volume}\n"
            f"Максимальная цена за 24 часа: {high_24h}\n"
            f"Минимальная цена за 24 часа: {low_24h}"
        )
        await message.answer(ticker_message)
    else:
        await message.answer("Не удалось получить данные о тикере.")

async def main():
    dp.include_router(router)  # Включение маршрутизатора для бота
    asyncio.create_task(connect_to_gateio())  # Запуск WebSocket подключения
    await dp.start_polling(bot, skip_updates=True)

if __name__ == '__main__':
    asyncio.run(main())















