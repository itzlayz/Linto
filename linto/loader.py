# █ ▀█▀ ▀█ █   ▄▀█ █▄█ ▀█
# █ ░█░ █▄ █▄▄ █▀█ ░█░ █▄
# https://t.me/itzlayz
#
# 🔒 Licensed under the GNU AGPLv3
# https://www.gnu.org/licenses/agpl-3.0.html

import typing

from importlib.abc import SourceLoader
from importlib.machinery import ModuleSpec

from discord.ext import commands
from .utils import rand


class StringLoader(SourceLoader):
    def __init__(self, data: str, origin: str) -> None:
        self.data = data.encode("utf-8")
        self.origin = origin

    def get_code(self, full_name: str) -> typing.Union[typing.Any, None]:
        if source := self.get_source(full_name):
            return compile(source, self.origin, "exec", dont_inherit=True)
        else:
            return None

    def get_filename(self, _) -> str:
        return self.origin

    def get_data(self, _) -> str:
        return self.data


def get_spec(source: str) -> ModuleSpec:
    """
    Makes spec for string module
    :param source: Module's source code
    :return: ModuleSpec
    """
    name = "linto.modules." + rand(5)
    origin = "<string>"

    return ModuleSpec(name, StringLoader(source, origin), origin=origin)


async def load_string(bot: commands.Bot, spec: ModuleSpec):
    name = bot._resolve_name(spec.name, False)
    bot.__extensions = getattr(bot, "__extensions", {})
    if name in bot.__extensions:
        raise commands.errors.ExtensionAlreadyLoaded(name)

    await bot._load_from_module_spec(spec, name)
    module = getattr(spec, dir(spec)[0])
    if issubclass(module, commands.Cog):
        return module.__name__

    return name
