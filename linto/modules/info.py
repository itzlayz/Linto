# █ ▀█▀ ▀█ █   ▄▀█ █▄█ ▀█
# █ ░█░ █▄ █▄▄ █▀█ ░█░ █▄
# https://t.me/itzlayz
                    
# 🔒 Licensed under the GNU AGPLv3
# https://www.gnu.org/licenses/agpl-3.0.html 

from discord.ext import commands

class Info(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
    
    @commands.command(aliases=["linto"])
    async def info(self, ctx):
        modules = len(self.bot.cogs)
        guilds = len((await self.bot.fetch_guilds(with_counts=False)))

        await ctx.reply(
            self.translations["owner"].format(self.bot.user) +
            self.translations["modules"].format(modules) +
            self.translations["guilds"].format(guilds)
        )

    @commands.command(aliases=["weburl", "web_url"])
    async def webmanager(self, ctx):
        await ctx.reply(f"`{self.bot.webmanager._url}`")

async def setup(bot):
    await bot.add_cog(Info(bot))