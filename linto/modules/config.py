from discord.ext import commands
from ..database import Database

from ..utils import strtobool


class ModuleConfig(dict):
    def __init__(self, module_name: str, config_dict: dict, database: Database):
        self.module_name = module_name
        self.config_dict = config_dict
        self.db = database

        self.__preload()

    def __preload(self):
        for key, default_value in self.config_dict.items():
            if key not in self:
                self[key] = self.db.get(self.module_name, key, default_value)

    def __getitem__(self, key: str):
        if key not in self:
            self.__preload()
        return super().__getitem__(key)

    def __setitem__(self, key: str, value) -> None:
        super().__setitem__(key, value)
        self.db.set(self.module_name, key, value)

    def get(self, key: str, default=None):
        return self[key] if key in self else default


class Config(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(aliases=["show_config", "sconfig"])
    async def showconfig(self, ctx):
        for module in self.bot.cogs.values():
            if hasattr(module, "config") and isinstance(module.config, dict):
                if not hasattr(module, "modified_config"):
                    module.modified_config = ModuleConfig(
                        module.qualified_name, module.config, self.db
                    )

        configs = [
            module.modified_config
            for module in self.bot.cogs.values()
            if (hasattr(module, "config")) and isinstance(module.config, dict)
        ]

        text = "```ini\n"
        for config in configs:
            text += f"[ {config.module_name} ]:\n"
            text += "\n".join(
                f"→ {config.module_name}.{k}: {str(v)} ({type(v).__name__})"
                for k, v in config.items()
            )
            text += "\n"

        text += "\n```"
        await ctx.reply(text)

    @commands.command(aliases=["edit_config", "econfig"])
    async def editconfig(self, ctx, key: str, value: str = None):
        if not value:
            return await ctx.reply(self.translations["pass_value"])

        parts = key.split(".")
        if len(parts) != 2:
            return await ctx.reply(self.translations["invalid_key"])

        module_name, key = parts
        if module_name not in self.bot.cogs:
            return await ctx.reply(self.translations["invalid_module"])

        module = self.bot.cogs[module_name]
        config = getattr(module, "modified_config", None)
        if not config:
            return await ctx.reply(self.translations["no_config"])

        if key not in config:
            return await ctx.reply(self.translations["no_key"])

        if isinstance(config[key], bool):
            try:
                value = bool(strtobool(value))
            except ValueError:
                return await ctx.reply(
                    self.translations["invalid_value"].format("bool")
                )
        elif isinstance(config[key], int):
            try:
                value = int(value)
            except ValueError:
                return await ctx.reply(self.translations["invalid_value"].format("int"))

        config[key] = value
        await ctx.reply(self.translations["sucessful"].format(key))
