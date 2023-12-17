
# █ ▀█▀ ▀█ █   ▄▀█ █▄█ ▀█
# █ ░█░ █▄ █▄▄ █▀█ ░█░ █▄
# https://t.me/itzlayz
                    
# 🔒 Licensed under the GNU AGPLv3
# https://www.gnu.org/licenses/agpl-3.0.html 

import io

from discord import File
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
        if len(output) <= 2000:
            output = f"```py\n{output}\n```"

        await ctx.reply(output)

async def setup(bot):
    await bot.add_cog(Eval(bot))