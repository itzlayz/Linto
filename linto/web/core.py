# █ ▀█▀ ▀█ █   ▄▀█ █▄█ ▀█
# █ ░█░ █▄ █▄▄ █▀█ ░█░ █▄
# https://t.me/itzlayz
#                           
# 🔒 Licensed under the GNU AGPLv3
# https://www.gnu.org/licenses/agpl-3.0.html

import re
import os
import sys
import jinja2
import asyncio
import logging
import aiohttp_jinja2

from .. import utils

from aiohttp import web
from discord.ext.commands import Bot, errors

class WebManager:
    def __init__(self, bot: Bot) -> None:
        self.app = web.Application()
        self.password = None
        self._url = None
        self.bot = bot
        
        aiohttp_jinja2.setup(
            self.app,
            loader=jinja2.FileSystemLoader(
                "linto/web/resources")
        )
        self.app["static_root_url"] = "/static"
        self.app.router.add_static("/static/", "linto/web/resources/static")

        self.app.router.add_get("/", self.index)
        self.app.router.add_get("/login", self.login)
        
        self.app.router.add_post("/unload", self.unload)
        self.app.router.add_post("/chpass", self.changePassword)
        self.app.router.add_post("/authorize", self.authorize)
        self.app.router.add_post("/consuming", self.consuming)
        self.app.router.add_post("/restart", self.restart)
        self.app.router.add_post("/eval", self.eval)
    
    @aiohttp_jinja2.template("index.html")
    async def index(self, _):
        cogs = [(k, v.description or "No description") for k, v in self.bot.cogs.items()]
        return {"cogs": cogs}

    @aiohttp_jinja2.template("login.html")
    async def login(self, _):
        return {}

    async def checkAuth(self, request: web.Request):
        data = await request.json()
        password = str(data.get("linto", "")).strip()
        if not password or password != self.password:
            return False
        
        return True

    async def changePassword(self, request: web.Request):
        data = await request.json()
        password = data["password"]
        curpass = data.get("curpassword", "")

        if not curpass or curpass != self.password:
            return web.Response(status=401)

        self.password = password
        self.bot.db.set("linto_web", "password", password)

        return web.Response()

    async def authorize(self, request: web.Request):
        if not self.password:
            self.password = self.bot.db.get(
                "linto_web", "password", "linto123")

        data = await request.json()
        password = str(data["linto"]).strip()
        if password != self.password:
            password = request.cookies.get("linto", "")
            if not password or password != self.password:
                return web.Response(status=401)
        
        return web.Response()
    
    async def unload(self, request: web.Request):
        if not self.checkAuth(request):
            return web.Response(status=401)
        
        data = await request.json()

        cog = data["cog"]
        cog = "linto.modules." + cog.lower()
        
        try:
            await self.bot.unload_extension(cog)
        except errors.ExtensionNotLoaded:
            pass
        
        logging.info(f"Unloaded {cog} module at web manager")
        return web.Response()

    async def restart(self, _):
        if not self.checkAuth(_):
            return web.Response(status=401)
        
        def _restart():
            os.execl(sys.executable, sys.executable, "-m", "linto")

        utils._atexit(_restart)
        logging.info("Restart invoked at web manager")
        
        sys.exit(0)

    async def eval(self, request: web.Request):
        if not self.checkAuth(request):
            return web.Response(status=401)
        
        data = await request.json()
        code = data["code"]
        output = await utils.epc(code, {"bot": self.bot})
        return web.Response(text=str(output).strip())

    async def consuming(self, _):
        cpu = utils.get_cpu()
        mem = utils.get_ram()
        
        data = {"memory": mem, "cpu": cpu}
        return web.json_response(data)

    async def start(self, port: int):
        logging.info("Starting web manager")
        self.password = self.bot.db.get(
            "linto_web", "password", None) or utils.rand()
        
        self.bot.db.set(
            "linto_web", "password", self.password)

        self.app_runner = web.AppRunner(self.app)
        await self.app_runner.setup()
        
        self.website = web.TCPSite(self.app_runner, None, port)
        self.port = port

        await self.website.start()
        await self.tunnel(port)

    async def tunnel(self, port: int):
        self.proc = await asyncio.create_subprocess_shell(
            (
                "ssh -o StrictHostKeyChecking=no -R "
                f"80:127.0.0.1:{port} nokey@localhost.run"
            ),
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        self._tunnel_event = asyncio.Event()
        async def get_url(stream):
            for getline in iter(stream.readline, ""):
                await asyncio.sleep(1)
                data_chunk = (await getline).decode()
                regex = r"tunneled.*?(https:\/\/.+)"
                if re.search(regex, data_chunk):
                    self._url = re.search(regex, data_chunk)[1]
                    if not self._tunnel_event.is_set():
                        self._tunnel_event.set()

        asyncio.ensure_future(get_url(self.proc.stdout))
        try:
            await asyncio.wait_for(self._tunnel_event.wait(), 15)
        except:
            self.proc.terminate()
            self._url = f"http://localhost:{port}"
        
        logging.info(f"Web manager on {self._url}")