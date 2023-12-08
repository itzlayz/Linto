import discord
import logging
import os

from . import __version__
from .localization import Translations
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
    bot.command_prefix = bot.db.get("linto", "prefix", ">")

    try:
        import git
        repo = git.Repo()

        _hash = repo.head.commit.hexsha
        diff = str(repo.git.rev_parse("HEAD")) == _hash

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
    
    for module in os.listdir("linto/modules"):
        if module.endswith(".py"):
            module = "linto.modules." + module[:-3]
            try:
                await bot.load_extension(module)
            except commands.errors.ExtensionAlreadyLoaded:
                await bot.unload_extension(module)
                await bot.load_extension(module)
            finally:
                if bot.extensions and module in bot.extensions:
                    translations = Translations(bot.db, module.split('.')[-1])
                    setattr(
                        getattr(
                            bot.extensions[module],
                            dir(bot.extensions[module])[0]
                        ),
                        "translations", 
                        translations
                    )

    port = gen_port()
    await bot.webmanager.start(port)

@bot.command()
async def reload(ctx):
    text = ""
    for module in os.listdir("linto/modules"):
        if module.endswith(".py"):
            module = "linto.modules." + module[:-3]
            try:
                await bot.load_extension(module)
                text += f":white_check_mark: **{module}**\n"
            except commands.errors.ExtensionAlreadyLoaded:
                await bot.unload_extension(module)
                await bot.load_extension(module)
                text += f":white_check_mark: **{module}**\n"
            except Exception as error:
                text += f":x: **{module}**: `{error}`\n"
            finally:
                if bot.extensions and module in bot.extensions:
                    translations = Translations(bot.db, module.split('.')[-1])
                    setattr(
                        getattr(
                            bot.extensions[module],
                            dir(bot.extensions[module])[0]
                        ),
                        "translations", 
                        translations
                    )
    
    await ctx.reply(text)