# █ ▀█▀ ▀█ █   ▄▀█ █▄█ ▀█
# █ ░█░ █▄ █▄▄ █▀█ ░█░ █▄
# https://t.me/itzlayz
#
# 🔒 Licensed under the GNU AGPLv3
# https://www.gnu.org/licenses/agpl-3.0.html

import importlib.util
import importlib.machinery

import traceback
import aiohttp
import typing
import json
import sys
import os

from discord.ext import commands
from discord import Message, File, AllowedMentions, GuildSticker, StickerItem

from .localization import Translations
from .client import logger, reload
from .database import Database

from typing import Sequence, Optional, Union
from types import MethodType
from io import BytesIO

errors = commands.errors
CogType = (commands.Cog, commands.cog.CogMeta)


def gen_port() -> int:
    import random, socket  # noqa: E401

    if "DOCKER" in os.environ:
        return 8080

    while port := random.randint(1024, 65536):
        if socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect_ex(
            ("localhost", port)
        ):
            break

    return port


def _is_submodule(parent: str, child: str) -> bool:
    return parent == child or child.startswith(parent + ".")


class Bot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.flet = None
        self.flet_app: bool = False

        self.webmanager = None
        self.db: Database = None

        self.remove_command("help")
        self._load_from_module_spec = MethodType(_load_from_module_spec, self)

    async def edit_bio(
        self,
        banner_color: int = 0,
        pronouns: str = "",
        bio: str = "",
    ) -> typing.List[typing.Optional[dict]]:
        """
        IMPORTANT:
        For example, if you pass the bio and pronouns with banner_color
        aren't passed, they will be replaced by default values.

        Avatar and username are not available because they need captcha.

        Edit bio without solving captcha:
        @me/profile - banner_color, pronouns, bio

        :param banner_color: Banner color in profile
        :param pronouns: Pronouns in profile
        :param bio: Biography in profile

        :return: All responses (avatar/global_name, banner_color/pronouns/bio)
        """
        responses = []
        async with aiohttp.ClientSession() as session:
            if banner_color or pronouns or bio:
                payload = {
                    k: v
                    for k, v in zip(
                        ["accent_color", "pronouns", "bio"],
                        [banner_color, pronouns, bio],
                    )
                    if v
                }
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": self.ws.token,
                }

                async with session.patch(
                    "https://discord.com/api/v9/users/%40me/profile",
                    data=json.dumps(payload),
                    headers=headers,
                ) as response:
                    response_json = await response.json()
                    responses.append({"name": "@me/profile", "json": response_json})

        return responses

    async def reload_extension(
        self, name: str, *, package: Optional[str] = None
    ) -> None:
        """From disnake"""
        name = self._resolve_name(name, package)
        lib = None

        try:
            lib = self.__extensions.get(name)
        except AttributeError:
            self.__extensions = {}

        if lib:
            modules = {
                name: module
                for name, module in sys.modules.items()
                if _is_submodule(lib.__name__, name)
            }

        try:
            try:
                await self.load_extension(name)
            except Exception:  # error -> unload
                await self.load_extension(name)
        except:
            if lib:
                lib.setup(self)
                self.__extensions[name] = lib

                sys.modules.update(modules)

            raise

    async def on_ready(self):
        self.add_command(reload)

        self.owner_id = self.user.id
        self.command_prefix = self.db.get("linto", "prefix", ">")

        logger.info(f"{self.user} is ready to use")
        for module in os.listdir("linto/modules"):
            if module.endswith(".py"):
                module = "linto.modules." + module[:-3]
                try:
                    await self.load_extension(module)
                except commands.errors.ExtensionAlreadyLoaded:
                    await self.unload_extension(module)
                    await self.load_extension(module)
                except Exception:
                    traceback.print_exc()

        if self.flet_app:
            await self.flet(self)

    async def process_commands(self, message: Message, /):
        if message.author.bot:
            return

        ctx = await self.get_context(message)
        ctx.reply = MethodType(reply, ctx)

        await self.invoke(ctx)


def set_translations(cog: commands.Cog, db):
    name = cog.__name__.lower()

    cog.db = cog.database = db
    cog.translations = Translations(db, name)


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
    **kwargs,
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
        **kwargs,
    }

    if file:
        return await self.message.reply(file=File(fp=file, filename=file.name))

    if not kwargs["files"] and kwargs.get("file", None):
        kwargs.pop("files", None)

    return await self.message.reply(**kwargs)


async def _load_from_module_spec(
    self: commands.Bot, spec: importlib.machinery.ModuleSpec, key: str
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
        setup = getattr(lib, "setup")
    except AttributeError:
        try:
            module = get_module(lib)
            setup = get_setup(module)
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
        set_translations(module, self.db)

        try:
            self.__extensions[key] = lib
        except AttributeError:
            self.__extensions = {}
            self.__extensions[key] = lib


def get_module(lib: importlib.machinery.ModuleSpec):
    lib_dir = filter(
        lambda x: not x.startswith("__") and not x.endswith("__"), dir(lib)
    )

    for method in lib_dir:
        instance = getattr(lib, method, None)
        if isinstance(instance, CogType):
            return instance

    raise AttributeError("Attribute not found")


def get_setup(instance):
    async def setup(bot):
        await bot.add_cog(instance(bot))

    return setup
