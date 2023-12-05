import os
import logging
from discord.ext import commands

logger = logging.getLogger()
    
async def load_extensions(bot: commands.Bot, reload: bool = False):
    for module in os.listdir("linto/modules"):
        if module.endswith(".py"):
            try:
                await bot.load_extension("linto.modules." + module[:-3])
            except commands.errors.ExtensionAlreadyLoaded:
                if reload:
                    await bot.unload_extension("linto.modules." + module[:-3])
                    await bot.load_extension("linto.modules." + module[:-3])

            logger.info(f"Loaded {module[:-3]} module")