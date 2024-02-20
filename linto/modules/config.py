from discord.ext import commands
from ..database import Database

from sys import version_info

if version_info < (3, 12, 0):
    from distutils.util import strtobool
else:

    def strtobool(val):
        """Convert a string representation of truth to true (1) or false (0).

        True values are 'y', 'yes', 't', 'true', 'on', and '1'; false values
        are 'n', 'no', 'f', 'false', 'off', and '0'.  Raises ValueError if
        'val' is anything else.
        """
        val = val.lower()
        if val in ("y", "yes", "t", "true", "on", "1"):
            return 1
        elif val in ("n", "no", "f", "false", "off", "0"):
            return 0
        else:
            raise ValueError("invalid truth value %r" % (val,))


class ModuleConfig(dict):
    def __init__(self, module_name: str, config_dict: dict, database: Database):
        self.module_name = module_name
        self.config_dict = config_dict
        self.db = database

        super().__init__()
        for k, v in self.config_dict.items():
            super().__setitem__(k, self.db.get(self.module_name, k, v))

    def __getitem__(self, __key: str):
        return (
            super().__getitem__(__key)
            if __key in self
            else self.db.get(self.module_name, __key, None)
        )

    def __setitem__(self, __key: str, value) -> None:
        super().__setitem__(__key, value)
        self.db.set(self.module_name, __key, value)

    def get(self, __key: str, __default=None):
        try:
            return self[__key]
        except KeyError:
            return __default


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
