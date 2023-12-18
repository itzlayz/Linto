
# █ ▀█▀ ▀█ █   ▄▀█ █▄█ ▀█
# █ ░█░ █▄ █▄▄ █▀█ ░█░ █▄
# https://t.me/itzlayz
                    
# 🔒 Licensed under the GNU AGPLv3
# https://www.gnu.org/licenses/agpl-3.0.html 

import discord
from discord.ext import commands

from .. import utils

class Eval(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.description = "Evaluate python code"
    
    @commands.command(aliases=["e", "evaluate"])
    async def eval(self, ctx, *, code: str):
        output = await utils.epc(
            code,
            {
                "self": self,
                "bot": self.bot,
                "discord": discord,
                "commands": commands,
                "utils": utils,
                "ctx": ctx,
                "db": self.bot.db
            }
        )
        if len(str(output)) <= 2000:
            output = f"```py\n{output}\n```"

        await ctx.reply(output)

async def setup(bot):
    await bot.add_cog(Eval(bot))