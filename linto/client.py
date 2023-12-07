import discord
import logging
import os

from . import utils, __version__
from discord.ext import commands

def gen_port() -> int:
    import random, socket

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

bot = commands.Bot(command_prefix='>', self_bot=True)
bot.remove_command("help")

@bot.event
async def on_ready():
    bot.owner_id = bot.user.id
    try:
        import git
        repo = git.Repo()

        _hash = repo.head.commit.hexsha
        diff = repo.git.rev_parse("HEAD")

        version = ".".join(map(str, __version__))
        update = "Up to date" if not diff else "Update available"

        banner = (
            "█   █ █▄ █ ▀█▀ █▀█\n"
            "█▄▄ █ █ ▀█  █  █▄█\n"
        )
        
        print(
            f"{banner}\n"
            f"→ Git hash: {_hash[:7]}\n"
            f"→ Version: {version}\n",
            f"→ {update}"
        )  
    except:
        logging.exception("Git error, look for git in path")
    
    await utils.load_extensions(bot)

    port = gen_port()
    await bot.webmanager.start(port)

@bot.command()
async def reload(ctx):
    text = ""
    for module in os.listdir("linto/modules"):
        if module.endswith(".py"):
            try:
                await bot.load_extension("linto.modules." + module[:-3])
                text += f":white_check_mark: **{module[:-3]}**\n"
            except commands.errors.ExtensionAlreadyLoaded:
                await bot.unload_extension("linto.modules." + module[:-3])
                await bot.load_extension("linto.modules." + module[:-3])
                text += f":white_check_mark: **{module[:-3]}**\n"
            except Exception as error:
                text += f":x: **{module[:-3]}**: `{error}`\n"
    
    await ctx.reply(text)