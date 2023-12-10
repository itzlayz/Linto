
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
        
        try:
            await ctx.reply(f"```py\n{output}\n```")
        except:  # noqa: E722
            file = io.BytesIO(ctx.message.content.encode())
            file.name = "output.txt"

            await ctx.reply(file=File(file, filename=file.name))

async def setup(bot):
    await bot.add_cog(Eval(bot))