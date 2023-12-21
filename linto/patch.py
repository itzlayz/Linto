import importlib.util
import importlib.machinery

import sys

from discord.ext import commands
from discord import Message, File, AllowedMentions, GuildSticker, StickerItem

from typing import Sequence, Optional, Union
from types import MethodType
from io import BytesIO

errors = commands.errors
CogType = (commands.Cog, commands.cog.CogMeta)

class Bot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._load_from_module_spec = MethodType(_load_from_module_spec, self)

    async def process_commands(self, message: Message, /):
        if message.author.bot:
            return

        ctx = await self.get_context(message)
        ctx.reply = MethodType(reply, ctx)

        await self.invoke(ctx)

async def reply(
    self: commands.Context,
    content: Optional[str] = None,
    *,
    tts: bool = False,
    files: Sequence[File] = (),
    stickers: Sequence[Union[GuildSticker, StickerItem]] = (),
    delete_after: float = None,
    nonce: Union[str, int] = None,
    allowed_mentions: AllowedMentions = None,
    mention_author: bool = False,
    suppress_embeds: bool = False,
    silent: bool = False,
    **kwargs
) -> Message:
    file = None
    if content and len(content) > 2000:
        file = BytesIO(content.encode())
        file.name = "output.txt"

    kwargs = {
        "content": content,
        "tts": tts,
        "files": files,
        "stickers": stickers,
        "delete_after": delete_after,
        "nonce": nonce,
        "allowed_mentions": allowed_mentions,
        "mention_author": mention_author,
        "suppress_embeds": suppress_embeds,
        "silent": silent,
        **kwargs
    }

    if file:
        return await self.message.reply(file=File(fp=file, filename=file.name))
    
    if not kwargs["files"] and kwargs.get("file", None):
        kwargs.pop("files", None)

    return await self.message.reply(**kwargs)

async def _load_from_module_spec(
    self: commands.Bot, 
    spec: importlib.machinery.ModuleSpec, 
    key: str
) -> None:
    """Custom structure"""
    
    # precondition: key not in self.__extensions
    lib = importlib.util.module_from_spec(spec)
    sys.modules[key] = lib
    try:
        spec.loader.exec_module(lib)  # type: ignore
    except Exception as e:
        del sys.modules[key]
        raise errors.ExtensionFailed(key, e) from e

    try:
        setup = getattr(lib, 'setup')
    except AttributeError:
        try:
            setup = get_module(lib)
        except AttributeError:
            del sys.modules[key]
            raise errors.NoEntryPointError(key)

    try:
        await setup(self)
    except Exception as e:
        del sys.modules[key]
        await self._remove_module_references(lib.__name__)
        await self._call_module_finalizers(lib, key)
        raise errors.ExtensionFailed(key, e) from e
    else:
        try:
            self.__extensions[key] = lib
        except AttributeError:
            self.__extensions = {}
            self.__extensions[key] = lib

def get_module(lib: importlib.machinery.ModuleSpec):
    lib_dir = filter(
        lambda x: not x.startswith("__") and
          not x.endswith("__"), dir(lib)
    )
    
    for method in lib_dir:
        instance = getattr(lib, method, None)
        if isinstance(instance, CogType):
            async def setup(bot):
                await bot.add_cog(instance(bot))

            return setup

    raise AttributeError("Attribute not found")