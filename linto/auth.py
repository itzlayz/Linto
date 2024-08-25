# █ ▀█▀ ▀█ █   ▄▀█ █▄█ ▀█
# █ ░█░ █▄ █▄▄ █▀█ ░█░ █▄
# https://t.me/itzlayz
#
# 🔒 Licensed under the GNU AGPLv3
# https://www.gnu.org/licenses/agpl-3.0.html

import logging
import asyncio

from getpass import getpass
from aiohttp import ClientSession

from .qrcode_websockets import DiscordAuthWebsocket

class Unauthorized(Exception):
    """Raised when the login or password is invalid."""

class Auth:
    def __init__(self, use_qr: bool = True) -> None:
        self.no_qr = use_qr

        self.token: str = None
        self.session: ClientSession = ClientSession()

    async def authorize(self) -> None:
        if self.no_qr:
            while True:
                login = input("Enter login: ")
                password = getpass("Enter password: ")
                
                try:
                    if await self.login(login, password):
                        return
                except Unauthorized:
                    logging.error("Invalid login or password. Please try again.")
        else:
            await self.authorize_qr()

    async def authorize_qr(self):
        logging.info("Authorizing through qrcode (To authorize without qrcode use --no-qr param)")
        
        websocket = DiscordAuthWebsocket()

        try:
            await websocket.connect()
        except Exception:
            logging.error("Can't login with qrcode, captcha required. Authorizing manually...")
            
            self.no_qr = True
            await self.authorize()

            return

        await asyncio.wait_for(websocket.done.wait(), 60 * 15)
        self.token = websocket.token

        await self.session.close()
        del self.session

    async def login(self, login: str, password: str) -> bool:
        """
        :param login: The user's login (email).
        :param password: The user's password.
        :return: True if login is successful, False otherwise.
        
        :raises Unauthorized: If the login credentials are invalid.
        """
        payload = {
            "gift_code_sku_id": None,
            "login": login,
            "password": password,
            "login_source": None,
            "undelete": False,
        }
        url = "https://discord.com/api/v9/auth/login"

        async with self.session.post(url, json=payload, headers={"Content-Type": "application/json"}) as response:
            response_json = await response.json()

        if response_json.get("code"):
            raise Unauthorized("Invalid login or password")

        if response_json.get("mfa"):
            return await self.handle_mfa(response_json["ticket"])

        self.token = response_json.get("token")
        return True

    async def handle_mfa(self, ticket: str) -> bool:
        """
        Handle Multi-Factor Authentication (MFA) using TOTP.

        :param ticket: The MFA ticket from the initial login attempt.
        :return: True if MFA is successful, False otherwise.
        """
        payload = {
            "gift_code_sku_id": None,
            "login_source": None,
            "ticket": ticket,
            "code": "",
        }
        url = "https://discord.com/api/v9/auth/mfa/totp"

        logging.info("2FA example: 123456")

        while True:
            code = input("Enter 2FA code: ")

            if not self.is_valid_mfa_code(code):
                logging.error("Invalid 2FA code. Please try again.")
                continue

            payload["code"] = code
            async with self.session.post(url, json=payload) as response:
                response_json = await response.json()

            if response_json.get("code"):
                logging.error("Invalid 2FA code. Please try again.")
                continue

            self.token = response_json["token"]
            await self.session.close()

            logging.info("Success! Wait for loading...")

            return True

    @staticmethod
    def is_valid_mfa_code(code: str) -> bool:
        if len(code) != 6:
            logging.error("Length of the code must be 6.")
            return False
        if not code.isdigit():
            logging.error("The 2FA code must be numeric.")
            return False
        
        return True
