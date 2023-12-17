from discord.ext import commands
from discord import Message, File, AllowedMentions, GuildSticker, StickerItem

from typing import Sequence, Optional, Union
from types import MethodType
from io import BytesIO

class Bot(commands.Bot):
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

    return await self.message.reply(**kwargs)
