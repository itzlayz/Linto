# █ ▀█▀ ▀█ █   ▄▀█ █▄█ ▀█
# █ ░█░ █▄ █▄▄ █▀█ ░█░ █▄
# https://t.me/itzlayz
#
# 🔒 Licensed under the GNU AGPLv3
# https://www.gnu.org/licenses/agpl-3.0.html

import discord
import logging
import os

from discord.ext import commands


async def get(*args):
    return 9999


discord.utils._get_build_number = get
logger = logging.getLogger()


@commands.command()
async def reload(ctx: commands.Context):
    text = ""
    for count, module in enumerate(os.listdir("linto/modules"), start=1):
        if module.endswith(".py"):
            module_name = f"linto.modules.{module[:-3]}"
            try:
                await ctx.bot.reload_extension(module_name)
                text += f"`{count})` :white_check_mark: **{module_name}**\n"
            except commands.errors.ExtensionAlreadyLoaded:
                await ctx.bot.load_extension(module_name)
                text += f"`{count})` :white_check_mark: **{module_name}**\n"
            except Exception as error:
                text += f"`{count})` :x: **{module_name}**: `{error}`\n"

    await ctx.reply(text)
