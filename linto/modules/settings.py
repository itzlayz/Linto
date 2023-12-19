# █ ▀█▀ ▀█ █   ▄▀█ █▄█ ▀█
# █ ░█░ █▄ █▄▄ █▀█ ░█░ █▄
# https://t.me/itzlayz
                    
# 🔒 Licensed under the GNU AGPLv3
# https://www.gnu.org/licenses/agpl-3.0.html 

import logging
import aiohttp
import sys
import re
import os

from discord.ext import commands
from .. import utils, loader

class Settings(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.description = "Configure your selfbot"
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if hasattr(ctx.command, 'on_error'):
            return
        
        if isinstance(error, commands.errors.CommandNotFound):
            return
        
        await ctx.reply(
            self.translations["error"].format(
                ctx.message.content, error
            )
        )
    
    @commands.command()
    async def setprefix(self, ctx, prefix: str):
        if not prefix:
            return await ctx.reply(
                self.translations["noprefix"])
        
        self.bot.command_prefix = prefix
        self.bot.db.set("linto", "prefix", prefix)
        await ctx.reply(self.translations["chprefix"].format(prefix))
    
    @commands.command(aliases=["setlang"])
    async def setlanguage(self, ctx, language: str):
        languages = map(
            lambda x: x[:-4],
            self.bot.localization.languages
        )
        if not language or language not in languages:
            return await ctx.reply(
                self.translations["nolanguage"])
        
        self.bot.db.set("linto", "language", language)
        await ctx.reply(self.translations["chlanguage"].format(language))

    @commands.command(aliases=["lm", "loadmod"])
    async def loadmodule(self, ctx):
        reference = ctx.message.reference
        if not reference or not reference.resolved.attachments:
            return await ctx.reply(self.translations["noreply"])

        attachment = reference.resolved.attachments[0]
        if not attachment.filename.endswith(".py"):
            return await ctx.reply(self.translations["noreply"])

        source = await attachment.read()
        try:
            await loader.load_string(self.bot, loader.get_spec(source.decode()))
        except (commands.errors.ExtensionAlreadyLoaded, commands.errors.ClientException):
            return await ctx.reply(self.translations["alreadyloaded"])

        filename = attachment.filename[:-3]
        await ctx.reply(self.translations["loadedmod"].format(filename))
    
    @commands.command(aliases=["dlmod", "downloadmod"])
    async def dlink(self, ctx, link: str):
        session = aiohttp.ClientSession()
        response = None
        source = None

        async with session.get(link) as response:
            response.raise_for_status()
            source = await response.text()

        try:
            name = await loader.load_string(self.bot, loader.get_spec(source))
        except (commands.errors.ExtensionAlreadyLoaded, commands.errors.ClientException):
            return await ctx.reply(self.translations["alreadyloaded"])

        await session.close()
        await ctx.reply(self.translations["loadedmod"].format(name))
    
    @commands.command()
    async def setrepo(self, ctx, path: str = ""):
        pattern = r"[a-zA-Z]+/[a-zA-Z]+"
        if not re.match(pattern, path):
            path = "itzlayz/linto-modules"
            
            self.bot.db.set("linto.settings", "repo_path", path)
            return await ctx.reply(
                self.translations["defaultrepo"]
            )

        self.bot.db.set("linto.settings", "repo_path", path)
        await ctx.reply(self.translations["changedrepo"])
    
    @commands.command()
    async def dlrepo(self, ctx, module: str = ""):
        path = self.bot.db.get("linto.settings", "repo_path", "itzlayz/linto-modules")
        api_url = f"https://api.github.com/repos/{path}/git/trees/main"

        async with aiohttp.ClientSession() as session:
            response = await session.get(api_url)
            response = await response.json()

        if response.get("message", None):
            return await ctx.reply(self.translations["not_found"])

        files = [
            file["path"] for file in response["tree"]
            if file["path"].endswith(".py")
        ]

        if module not in files:
            return await ctx.reply(
                self.translations["module_list"].format(
                    path,
                    ", ".join(map(lambda x: f"`{x[:-3]}`", files))
                )
            )

        raw_link = f"https://raw.githubusercontent.com/{path}/main/{module}"

        async with aiohttp.ClientSession().get(raw_link) as source:
            source = await source.text()
            
            try:
                name = await loader.load_string(self.bot, loader.get_spec(source))
            except (commands.errors.ExtensionAlreadyLoaded, commands.errors.ClientException):
                return await ctx.reply(self.translations["alreadyloaded"])

        await ctx.reply(self.translations["loadedmod"].format(name))


    @commands.command(aliases=["latency"])
    async def ping(self, ctx):
        ping = str(round(self.bot.ws.latency * 1000, 2))
        await ctx.reply(self.translations["latency"].format(ping))

    @commands.command(aliases=["restartbot"])
    async def restart(self, ctx):
        def _restart():
            os.execl(sys.executable, sys.executable, "-m", "linto")

        utils._atexit(_restart)
        logging.info("Restarting")
        
        sys.exit(0)

async def setup(bot):
    await bot.add_cog(Settings(bot))