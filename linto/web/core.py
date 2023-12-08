# █ ▀█▀ ▀█ █   ▄▀█ █▄█ ▀█
# █ ░█░ █▄ █▄▄ █▀█ ░█░ █▄
# https://t.me/itzlayz
#                           
# 🔒 Licensed under the GNU AGPLv3
# https://www.gnu.org/licenses/agpl-3.0.html

import re
import jinja2
import asyncio
import logging
import aiohttp_jinja2

from aiohttp import web
from .. import utils
from discord.ext.commands import Bot, errors

class WebManager:
    def __init__(self, bot: Bot) -> None:
        self.app = web.Application()
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
        self.app.router.add_post("/reload", self.reload)
        self.app.router.add_post("/consuming", self.consuming)
        self.app.router.add_post("/eval", self.eval)
    
    @aiohttp_jinja2.template("index.html")
    async def index(self, _):
        cogs = [(k, v.description or "No description") for k, v in self.bot.cogs.items()]
        return {"cogs": cogs}
    
    async def reload(self, request: web.Request):
        data = await request.json()

        cog = data["cog"]
        cog = "linto.modules." + cog.lower()
        
        try:
            await self.bot.unload_extension(cog)
            await self.bot.load_extension(cog)
        except errors.ExtensionNotLoaded:
            await self.bot.load_extension(cog)
        
        logging.info(f"Reloaded {cog} module at web manager")
        return web.Response()

    async def eval(self, request: web.Request):
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