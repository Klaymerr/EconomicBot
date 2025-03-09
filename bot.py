import asyncio

from aiogram import Bot, Dispatcher
from rout import router
from secrets import bot_token

async def main() -> None:
    dp = Dispatcher()
    dp.include_router(router)
    bot = Bot(token=bot_token)

    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
