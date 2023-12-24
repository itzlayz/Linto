# █ ▀█▀ ▀█ █   ▄▀█ █▄█ ▀█
# █ ░█░ █▄ █▄▄ █▀█ ░█░ █▄
# https://t.me/itzlayz
#                           
# 🔒 Licensed under the GNU AGPLv3
# https://www.gnu.org/licenses/agpl-3.0.html

import asyncio
import warnings
import os


from discord.errors import LoginFailure
from .localization import Localization
from .database import Database
from .web import WebManager
from .client import bot
from .logger import init
from .auth import Auth

logger = init()

async def _main():
    if "token.txt" not in os.listdir():
        prompt = input("Enter a token or continue to authorize manually: ")
        if not prompt.strip():
            auth = Auth()
            await auth.authorize()

            with open("token.txt", "w") as file:
                file.write(auth.token)

            del auth
            await _main()
    else:
        with open("token.txt", "r") as file:
            token = file.read()
        
        try:
            await bot.login(token)
        except LoginFailure:
            os.remove("token.txt")
            await _main()

    web = WebManager(bot)
    bot.webmanager = web

    database = Database("config.json")
    bot.db = bot.config = database

    localization = Localization(database)
    bot.translations = bot.localization = localization
    
    await bot.connect()

def main():
    warnings.filterwarnings("ignore")
    asyncio.run(_main())
