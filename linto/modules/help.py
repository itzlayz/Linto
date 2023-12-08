# █ ▀█▀ ▀█ █   ▄▀█ █▄█ ▀█
# █ ░█░ █▄ █▄▄ █▀█ ░█░ █▄
# https://t.me/itzlayz
                    
# 🔒 Licensed under the GNU AGPLv3
# https://www.gnu.org/licenses/agpl-3.0.html 

from discord.ext import commands

class Help(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
    
    @commands.command()
    async def help(self, ctx):
        help_message = self.translations["cmdlist"]

        for cog_name, cog in self.bot.cogs.items():
            command_names = [cmd.name for cmd in cog.get_commands()]
            commands_list = ", ".join([f"`{cmd}`" for cmd in command_names])
            help_message += f"## {cog_name.title()}:\n- {commands_list}\n\n"

        await ctx.send(help_message)

async def setup(bot):
    await bot.add_cog(Help(bot))
