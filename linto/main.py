import asyncio
import warnings
import os

from discord.errors import LoginFailure

from .localization import Localization
from .database import Database
from .web import WebManager
from .patch import Bot as patchBot
from .logger import init
from .auth import Auth

from . import utils, __version__

logger = init()

class Linto:
    def __init__(self):
        self.loop = None
        self.tokens = []

    def linto_badge(self):
        _hash = utils.git_sha
        diff = utils.git_diff()

        _version = ".".join(map(str, __version__))
        update = "Up to date" if not diff else "Update available"

        banner = (
            "█   █ █▄ █ ▀█▀ █▀█\n"
            "█▄▄ █ █ ▀█  █  █▄█\n"
        )
        
        print(
            f"{banner}\n"
            f"→ Git hash: {_hash[:7]}\n"
            f"→ Version: {_version}\n"
            f"→ {update}\n"
        )

    async def run_bot(self, token):
        try:
            client = patchBot(command_prefix=">", self_bot=True)
            _id = token.split('.')[0][:7]

            web = WebManager(client)
            client.webmanager = web

            database = Database(f"config-{_id}.json")
            client.db = client.config = database

            localization = Localization(database)
            client.translations = client.localization = localization
            
            await client.login(token)
            await client.connect()
        except LoginFailure:
            hint = token.split('.')[0]
            logger.error(f"Login failure during login ({hint}...)")

    async def amain(self):
        self.loop = asyncio.get_running_loop()
        if "token.txt" not in os.listdir():
            prompt = input("Enter a token or continue to authorize manually: ")
            if not prompt.strip():
                auth = Auth()
                await auth.authorize()

                with open("token.txt", "w") as file:
                    file.write(auth.token)

                del auth
                await self.amain()
        else:
            self.linto_badge()
            with open("token.txt", "r") as file:
                self.tokens = [token.strip() for token in file.readlines()]

            tasks = [self.run_bot(token) for token in self.tokens]
            await asyncio.gather(*tasks)

    def main(self):
        warnings.filterwarnings("ignore")
        asyncio.run(self.amain())

def main():
    linto = Linto()
    linto.main()
