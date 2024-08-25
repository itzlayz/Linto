# █ ▀█▀ ▀█ █   ▄▀█ █▄█ ▀█
# █ ░█░ █▄ █▄▄ █▀█ ░█░ █▄
# https://t.me/itzlayz
#
# 🔒 Licensed under the GNU AGPLv3
# https://www.gnu.org/licenses/agpl-3.0.html

import asyncio
import warnings

import pathlib

from discord.errors import LoginFailure
from getpass import getpass

from .localization import Localization
from .patch import Bot as PatchBot
from .database import Database
from .flet import init_flet
from .logger import init
from .auth import Auth

from . import utils, __version__

logger = init()

def parse(parser, key):
    return getattr(parser, key, False)

class Linto:
    def __init__(self, parser):
        self.loop: asyncio.AbstractEventLoop = None
        self.tokens: list[str] = []

        self.parser = parser

        self.flet_app: bool = parse(parser, "flet_app")
        self.no_web: bool = parse(parser, "no_web")
        self.no_qr: bool = parse(parser, "no_qr")

    def display_linto_badge(self):
        git_hash = utils.git_sha
        git_diff = utils.git_diff()

        version = ".".join(map(str, __version__))
        update_status = "Up to date" if not git_diff else "Update available"

        with open("assets/banner.txt") as banner_file:
            banner = banner_file.read()

        print(
            f"{banner}\n"
            f"→ Git hash: {git_hash[:7]}\n"
            f"→ Version: {version}\n"
            f"→ {update_status}\n"
        )

    async def run_bot(self, token: str):
        try:
            client = PatchBot(command_prefix=">")
            client_id = token.split(".")[0][:7]

            client.flet_app = self.flet_app
            if self.flet_app:
                client.flet = init_flet

            database = Database(f"config-{client_id}.json")
            client.db = client.config = database

            localization = Localization(database)
            client.translations = client.localization = localization

            await client.login(token)
            await client.connect()
        except LoginFailure:
            token_hint = token.split(".")[0]
            logger.error(f"Login failure during login ({token_hint}...)")
        except Exception as e:
            logger.error(f"Unexpected error during bot run: {str(e)}")

    async def get_tokens(self) -> list[str]:
        """
        Get tokens from 'token.txt' or prompt the user for a token if the file doesn't exist.

        :return: List of tokens
        """
        tokens = pathlib.Path("token.txt")

        if not tokens.exists() or not tokens.read_text().strip():
            token = getpass("Enter a token or continue to authorize manually: ").strip()
            if not token:
                await self.authorize_manually()
            else:
                return [token]
        else:
            return [token.strip() for token in tokens.read_text().splitlines()]

    async def authorize_manually(self):
        auth = Auth(self.no_qr)
        await auth.authorize()

        with open("token.txt", "w") as token_file:
            token_file.write(auth.token)

        del auth
        await self.amain()

    async def amain(self):
        self.loop = asyncio.get_running_loop()
        self.tokens = await self.get_tokens()

        tasks = [self.run_bot(token) for token in self.tokens]
        await asyncio.gather(*tasks)

    def main(self):
        warnings.filterwarnings("ignore")
        self.display_linto_badge()
        asyncio.run(self.amain())


def main(parser):
    linto = Linto(parser)
    linto.main()
