# █ ▀█▀ ▀█ █   ▄▀█ █▄█ ▀█
# █ ░█░ █▄ █▄▄ █▀█ ░█░ █▄
# https://t.me/itzlayz
                    
# 🔒 Licensed under the GNU AGPLv3
# https://www.gnu.org/licenses/agpl-3.0.html 

from discord.ext import commands

class Help(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.description = "Show all commands"
    
    @commands.command()
    async def help(self, ctx):
        help_message = "```ini\n" + self.translations["cmdlist"] + "\n"
        prefix = self.bot.command_prefix
        
        sorted_cogs = sorted(self.bot.cogs.items(), key=lambda x: len(x[0]))
        for cog_name, cog in sorted_cogs:
            command_names = [cmd.name for cmd in cog.get_commands()]
            commands_list = ", ".join([f"{prefix}{cmd}" for cmd in command_names])

            if commands_list:
                help_message += f"[ {cog_name.title()} ]: {commands_list}\n"

        help_message += "\n```"
        await ctx.send(help_message)