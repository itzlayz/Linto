import importlib.util
import importlib.machinery
import traceback
import aiohttp
import typing
import json
import sys
import os
import random
import socket

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

DEFAULT_PORT = 8080
MIN_PORT = 1024
MAX_PORT = 65536

DISCORD_PROFILE_URL = "https://discord.com/api/v9/users/%40me/profile"

def generate_available_port() -> int:
    """
    Generate a random available port. If running in a Docker environment, return a default port.
    """
    if "DOCKER" in os.environ:
        return DEFAULT_PORT

    while port := random.randint(MIN_PORT, MAX_PORT):
        if socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect_ex(("localhost", port)):
            return port

def is_submodule(parent: str, child: str) -> bool:
    """
    Check if the given child module is a submodule of the parent module.
    """
    return parent == child or child.startswith(f"{parent}.")

class Bot(commands.Bot):
    def __init__(self, *args, **kwargs):
        kwargs["self_bot"] = True
        
        super().__init__(*args, **kwargs)

        self._extensions = {}

        self.flet = None
        self.flet_app: bool = False
        self.webmanager = None
        self.db: Database = None

        self.remove_command("help")
        self._load_from_module_spec = MethodType(load_from_module_spec, self)

    async def edit_bio(self, banner_color: int = 0, pronouns: str = "", bio: str = "") -> typing.List[Optional[dict]]:
        """
        Edit the user's Discord profile bio, pronouns, and banner color.

        :param banner_color: Banner color in profile
        :param pronouns: Pronouns in profile
        :param bio: Biography in profile
        :return: List of responses containing the modified profile information
        """
        responses = []
        async with aiohttp.ClientSession() as session:
            if banner_color or pronouns or bio:
                payload = {k: v for k, v in zip(["accent_color", "pronouns", "bio"], [banner_color, pronouns, bio]) if v}
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": self.ws.token,
                }

                async with session.patch(DISCORD_PROFILE_URL, data=json.dumps(payload), headers=headers) as response:
                    response_json = await response.json()
                    responses.append({"name": "@me/profile", "json": response_json})

        return responses

    async def reload_extension(self, name: str, *, package: Optional[str] = None) -> None:
        """
        Reload the specified extension. If it fails, try to unload and load it again.

        :param name: Name of the extension to reload
        :param package: Optional package name
        """
        name = self._resolve_name(name, package)
        module_instance = self.extensions.get(name)

        if module_instance:
            modules = {name: module for name, module in sys.modules.items() if is_submodule(module_instance.__name__, name)}

        try:
            await self.unload_extension(name)
        except commands.ExtensionNotLoaded:
            pass

        await self.load_extension(name)  
        if module_instance:
            module_instance.setup(self)
            self._extensions[name] = module_instance
            sys.modules.update(modules)

    async def on_ready(self):
        """
        Event handler for when the bot is ready.
        """
        self.add_command(reload)

        self.owner_id = self.user.id
        self.command_prefix = self.db.get("linto", "prefix", ">")

        logger.info(f"{self.user} is ready to use")
        for module in os.listdir("linto/modules"):
            if module.endswith(".py"):
                module_name = f"linto.modules.{module[:-3]}"
                try:
                    await self.load_extension(module_name)
                except commands.errors.ExtensionAlreadyLoaded:
                    await self.unload_extension(module_name)
                    await self.load_extension(module_name)
                except Exception:
                    traceback.print_exc()

        if self.flet_app:
            await self.flet(self)

    async def process_commands(self, message: Message, /):
        """
        Process commands from the incoming message.

        :param message: The message to process
        """
        if message.author.bot:
            return

        ctx = await self.get_context(message)
        ctx.reply = MethodType(reply, ctx)

        await self.invoke(ctx)

def set_translations(cog: commands.Cog, db: Database):
    """
    Set the translations for the given cog using the provided database.

    :param cog: The cog to set translations for
    :param db: The database instance to use for translations
    """
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
    delete_after: Optional[float] = None,
    nonce: Union[str, int] = None,
    allowed_mentions: AllowedMentions = None,
    mention_author: bool = False,
    suppress_embeds: bool = False,
    silent: bool = False,
    **kwargs,
) -> Message:
    """
    Reply to a message in a Discord context, with additional functionality like file attachments.

    :param content: The content of the reply
    :param tts: Whether to use text-to-speech
    :param files: Files to attach to the reply
    :param stickers: Stickers to include in the reply
    :param delete_after: Delete the reply after a certain time
    :param nonce: Nonce for the reply
    :param allowed_mentions: Allowed mentions settings
    :param mention_author: Whether to mention the author of the original message
    :param suppress_embeds: Whether to suppress embeds in the reply
    :param silent: Whether the reply should be silent
    :return: The message that was sent as a reply
    """
    file = None
    if content and len(content) > 2000:
        file = BytesIO(content.encode())
        file.name = "output.txt"

    kwargs.update({
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
    })

    if file:
        return await self.message.reply(file=File(fp=file, filename=file.name))

    if not kwargs["files"] and kwargs.get("file", None):
        kwargs.pop("files", None)

    return await self.message.reply(**kwargs)

async def load_from_module_spec(self: commands.Bot, spec: importlib.machinery.ModuleSpec, key: str) -> None:
    """
    Load a module from its spec and handle the setup process.

    :param spec: The module spec to load from
    :param key: The key to associate with the loaded module
    """
    module_instance = importlib.util.module_from_spec(spec)
    sys.modules[key] = module_instance

    try:
        spec.loader.exec_module(module_instance)
    except Exception as e:
        del sys.modules[key]
        raise commands.ExtensionFailed(key, e) from e

    try:
        setup = getattr(module_instance, "setup")
    except AttributeError:
        try:
            module_instance = get_cog_module(module_instance)
            setup = get_cog_setup_function(module_instance)
        except AttributeError:
            del sys.modules[key]
            raise commands.NoEntryPointError(key)

    try:
        await setup(self)
    except Exception as e:
        del sys.modules[key]
        await self._remove_module_references(module_instance.__name__)
        await self._call_module_finalizers(module_instance, key)
        raise commands.ExtensionFailed(key, e) from e
    else:
        set_translations(module_instance, self.db)
        self._extensions[key] = module_instance 

def get_cog_module(lib: importlib.machinery.ModuleSpec):
    """
    Retrieve the first cog module from the given library module.

    :param lib: The library module to search in
    :return: The cog module instance found
    :raises AttributeError: If no cog module is found
    """
    for method in dir(lib):
        if not method.startswith("__"):
            instance = getattr(lib, method, None)
            if isinstance(instance, CogType):
                return instance

    raise AttributeError("No cog module found in the library.")

def get_cog_setup_function(instance):
    """
    Create a setup function for the given cog instance.

    :param instance: The cog instance to create the setup function for
    :return: The setup function
    """
    async def setup(bot):
        await bot.add_cog(instance(bot))

    return setup
