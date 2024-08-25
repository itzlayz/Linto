# Based on https://raw.githubusercontent.com/malmeloo/Discord-QR-Auth-Client/master/server.py

import base64
import json
import asyncio
import aiohttp
import websockets
import logging

from qrcode.main import QRCode

from Crypto.Cipher import PKCS1_OAEP
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA

class Messages:
    HEARTBEAT = "heartbeat"
    HELLO = "hello"
    INIT = "init"
    NONCE_PROOF = "nonce_proof"
    PENDING_REMOTE_INIT = "pending_remote_init"
    PENDING_TICKET = "pending_ticket"
    PENDING_LOGIN = "pending_login"

class DiscordAuthWebsocket:
    WS_ENDPOINT = "wss://remote-auth-gateway.discord.gg/?v=2"
    LOGIN_ENDPOINT = "https://discord.com/api/v9/users/@me/remote-auth/login"

    def __init__(self):
        self.key = RSA.generate(2048)
        self.cipher = PKCS1_OAEP.new(self.key, hashAlgo=SHA256)

        self.heartbeat_interval = None
        self.last_heartbeat = None

        self.token = None
        self.done = asyncio.Event()

    @property
    def public_key(self):
        pub_key = self.key.publickey().export_key().decode("utf-8")
        pub_key = "".join(pub_key.split("\n")[1:-1])

        return pub_key

    async def heartbeat_sender(self):
        while True:
            await asyncio.sleep(0.5)
            current_time = asyncio.get_event_loop().time()

            if (current_time - self.last_heartbeat + 1) >= self.heartbeat_interval:
                try:
                    await self.send(Messages.HEARTBEAT)
                except websockets.ConnectionClosed:
                    return
                
                self.last_heartbeat = current_time

    async def send(self, op, data=None):
        payload = {"op": op}
        if data:
            payload.update(data)

        await self.ws.send(json.dumps(payload))

    async def exchange_ticket(self, ticket):
        async with aiohttp.ClientSession() as session:
            async with session.post(self.LOGIN_ENDPOINT, json={"ticket": ticket}) as response:
                data = await response.json()
                token = data.get("encrypted_token")

                if not token and data.get("captcha_key"):
                    raise Exception("Captcha required :(")
                
    def decrypt_payload(self, encrypted_payload):
        payload = base64.b64decode(encrypted_payload)
        decrypted = self.cipher.decrypt(payload)

        return decrypted
    
    def process_qr(self, fingerprint):
        qr = QRCode(error_correction=1)

        qr.add_data(f"https://discordapp.com/ra/{fingerprint}")
        qr.make(fit=True)
        
        qr.print_ascii()

    async def on_message(self, message):
        data = json.loads(message)
        op = data.get("op")

        if op == Messages.HELLO:
            self.heartbeat_interval = data.get("heartbeat_interval") / 1000
            self.last_heartbeat = asyncio.get_event_loop().time()
            asyncio.create_task(self.heartbeat_sender())

            await self.send(Messages.INIT, {"encoded_public_key": self.public_key})
        elif op == Messages.NONCE_PROOF:
            nonce = data.get("encrypted_nonce")
            decrypted_nonce = self.decrypt_payload(nonce)
            proof = SHA256.new(data=decrypted_nonce).digest()
            proof = base64.urlsafe_b64encode(proof).decode().rstrip("=")

            # so strange thing btw
            # while reversing i saw "nonce" instead of "proof" key, 
            # but it give handshake error lol

            await self.send(Messages.NONCE_PROOF, {"proof": proof})
        elif op == Messages.PENDING_REMOTE_INIT:
            fingerprint = data.get("fingerprint")
            self.process_qr(fingerprint)
        elif op == Messages.PENDING_TICKET:
            encrypted_payload = data.get("encrypted_user_payload")
            payload = self.decrypt_payload(encrypted_payload).decode()

            logging.info(f"Processing user `{payload.split(':')[-1]}`")
        elif op == Messages.PENDING_LOGIN:
            ticket = data.get("ticket")
            encrypted_token = await self.exchange_ticket(ticket)

            if encrypted_token:
                token = self.decrypt_payload(encrypted_token)
                self.token = token.decode()
            else:
                print("\n\nNO TOKEN WTF\n\n")

            self.done.set()
            await self.ws.close()

    async def connect(self):
        async with websockets.connect(self.WS_ENDPOINT, extra_headers={"Origin": "https://discord.com"}) as ws:
            self.ws = ws
            async for message in ws:
                await self.on_message(message)
