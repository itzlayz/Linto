import asyncio
import os

from .web import WebManager
from .client import bot
from .logger import init

logger = init()

async def _main():
    if "token.txt" not in os.listdir():
        token = input("Enter discord token: ")
    else:
        with open("token.txt", "r") as file:
            token = file.read()

        if not token:
            os.remove("token.txt")
            await main()

    web = WebManager(bot)
    bot.webmanager = web
    
    await bot.start(token)

def main():
    asyncio.run(_main())
