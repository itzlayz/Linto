# █ ▀█▀ ▀█ █   ▄▀█ █▄█ ▀█
# █ ░█░ █▄ █▄▄ █▀█ ░█░ █▄
# https://t.me/itzlayz
                    
# 🔒 Licensed under the GNU AGPLv3
# https://www.gnu.org/licenses/agpl-3.0.html 

from discord.ext import commands

class Settings(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
    
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

async def setup(bot):
    await bot.add_cog(Settings(bot))