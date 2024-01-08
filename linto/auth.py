# █ ▀█▀ ▀█ █   ▄▀█ █▄█ ▀█
# █ ░█░ █▄ █▄▄ █▀█ ░█░ █▄
# https://t.me/itzlayz
#                           
# 🔒 Licensed under the GNU AGPLv3
# https://www.gnu.org/licenses/agpl-3.0.html

import typing
import logging

from getpass import getpass
from aiohttp import ClientSession

class Unauthorized(Exception):
    """
    Raised when provided with an invalid login or password
    """

class Auth:
    def __init__(self) -> None:
        self.token = None
        self.session = ClientSession()

    async def authorize(self):
        login = input("Enter login: ")
        password = getpass("Enter password: ")
        
        while True:
            try:
                status = await self.login(login, password)
                if status:
                    return
            except Unauthorized:
                break
        
        logging.error("Invalid login or password. Please try again.")
        await self.authorize()

    async def login(self, login: str, password: str):
        payload = {
            "gift_code_sku_id": None,
            "login": login,
            "password": password,
            "login_source": None,
            "undelete": False
        }
        url = "https://discord.com/api/v9/auth/login"

        async with self.session.post(
            url, json=payload, 
            headers={"Content-Type": "application/json"}
        ) as response:
            response = await response.json()

        if response.get("code", None):
            raise Unauthorized("Invalid login or password")
        
        if response["mfa"]:
            return await self.mfa(response["ticket"])
        
        return True
        
    async def mfa(self, ticket: str):
        payload = {
            "gift_code_sku_id": None,
            "login_source": None,
            "ticket": ticket,
            "code": ""
        }
        url = "https://discord.com/api/v9/auth/mfa/totp"

        logging.info('2FA example: 123456')
        while True:
            code = input("Enter 2FA code: ")
            try:
                int(code)

                if len(code) != 6:
                    logging.error(
                        "Length of the code must be 6."
                        "Please try again."
                    )
                    continue
            except ValueError:
                logging.error("Invalid 2FA. Please try again.")
                continue
            
            payload["code"] = code
            async with self.session.post(url, json=payload) as response:
                response = await response.json()

            if response.get("code", None):
                logging.error("Invalid 2FA. Please try again.")
                continue

            self.token = response["token"]
            await self.session.close()

            break

        return True
