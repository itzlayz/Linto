# █ ▀█▀ ▀█ █   ▄▀█ █▄█ ▀█
# █ ░█░ █▄ █▄▄ █▀█ ░█░ █▄
# https://t.me/itzlayz
                    
# 🔒 Licensed under the GNU AGPLv3
# https://www.gnu.org/licenses/agpl-3.0.html 

import git

from discord.ext import commands

from ..utils import iniFormatting
from .. import version, __version__

class Info(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.description = "Info about your account"
    
    @commands.command(aliases=["linto"])
    async def info(self, ctx):
        msg = await ctx.reply(iniFormatting("Loading..."))
        modules = len(self.bot.cogs)
        guilds = len((await self.bot.fetch_guilds(with_counts=False)))

        diff = git.Repo().git.log([f"HEAD..origin/{version.branch}", "--oneline"])

        _version = ".".join(map(str, __version__))
        update = self.translations["uptodate"] if not diff else self.translations["update"]

        await msg.edit(
            self.translations["version"].format(_version) + update +
            self.translations["owner"].format(self.bot.user) +
            self.translations["modules"].format(modules) +
            self.translations["guilds"].format(guilds) 
        )

    @commands.command(aliases=["weburl", "web_url"])
    async def webmanager(self, ctx):
        await ctx.reply(f"`{self.bot.webmanager._url}`")

async def setup(bot):
    await bot.add_cog(Info(bot))