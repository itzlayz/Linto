
# █ ▀█▀ ▀█ █   ▄▀█ █▄█ ▀█
# █ ░█░ █▄ █▄▄ █▀█ ░█░ █▄
# https://t.me/itzlayz
                    
# 🔒 Licensed under the GNU AGPLv3
# https://www.gnu.org/licenses/agpl-3.0.html 


from discord.ext import commands
from ..utils import epc

class Eval(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
    
    @commands.command(aliases=["e", "evaluate"])
    async def eval(self, ctx, *, code: str):
        output = await epc(
            code,
            {
                "self": self,
                "bot": self.bot,
                "ctx": ctx,
                "db": self.bot.db
            }
        )
        await ctx.reply(f"```py\n{output}\n```")

async def setup(bot):
    await bot.add_cog(Eval(bot))