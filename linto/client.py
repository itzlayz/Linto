# █ ▀█▀ ▀█ █   ▄▀█ █▄█ ▀█
# █ ░█░ █▄ █▄▄ █▀█ ░█░ █▄
# https://t.me/itzlayz
#                           
# 🔒 Licensed under the GNU AGPLv3
# https://www.gnu.org/licenses/agpl-3.0.html

import discord
import logging
import os

from . import __version__, patch, utils
from discord.ext import commands

def gen_port() -> int:
    import random, socket  # noqa: E401

    if "DOCKER" in os.environ:
        return 8080
    
    while port := random.randint(1024, 65536):
        if socket.socket(
            socket.AF_INET, 
            socket.SOCK_STREAM
        ).connect_ex(
            ("localhost", port)
        ):
            break

    return port

async def get(*args):
    return 9999

discord.utils._get_build_number = get
logger = logging.getLogger()

bot = patch.Bot(command_prefix='>', self_bot=True)
bot.remove_command("help")

@bot.event
async def on_ready():
    bot.owner_id = bot.user.id
    bot.command_prefix = bot.db.get("linto", "prefix", ">")

    _hash = utils.git_sha
    diff = utils.git_diff()

    _version = ".".join(map(str, __version__))
    update = "Up to date" if not diff else "Update available"

    banner = (
        "█   █ █▄ █ ▀█▀ █▀█\n"
        "█▄▄ █ █ ▀█  █  █▄█\n"
    )
    
    print(
        f"{banner}\n"
        f"→ Git hash: {_hash[:7]}\n"
        f"→ Version: {_version}\n"
        f"→ {update}\n"
    ) 
    
    for module in os.listdir("linto/modules"):
        if module.endswith(".py"):
            module = "linto.modules." + module[:-3]
            try:
                await bot.load_extension(module)
            except commands.errors.ExtensionAlreadyLoaded:
                await bot.unload_extension(module)
                await bot.load_extension(module)

    port = gen_port()
    await bot.webmanager.start(port)

@bot.command()
async def reload(ctx):
    text = ""
    count = 0
    for module in os.listdir("linto/modules"):
        if module.endswith(".py"):
            count += 1
            module = "linto.modules." + module[:-3]
            try:
                await bot.load_extension(module)
                text += f"`{count})` :white_check_mark: **{module}**\n"
            except commands.errors.ExtensionAlreadyLoaded:
                await bot.unload_extension(module)
                await bot.load_extension(module)
                text += f"`{count})` :white_check_mark: **{module}**\n"
            except Exception as error:
                text += f"`{count})` :x: **{module}**: `{error}`\n"
    
    await ctx.reply(text)