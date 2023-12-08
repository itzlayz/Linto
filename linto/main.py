import asyncio
import os

from .localization import Localization
from .database import Database
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

    database = Database("config.json")
    bot.db = bot.config = database

    localization = Localization(database)
    bot.translations = bot.localization = localization
    
    await bot.start(token)

def main():
    asyncio.run(_main())
