import aiohttp
import logging
import git

from discord.ext import commands, tasks
from ..utils import git_sha

logger = logging.getLogger(__name__)

class Notifier(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.url = "https://api.github.com/repos/itzlayz/linto/git/refs/heads/{}".format(
            git.Repo().active_branch.name
        )

        self.notified = False
        self.check_update.start()
    
    @tasks.loop(seconds=30.0)
    async def check_update(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url) as response:
                response = await response.json()

        commit_sha = response.get("object", {}).get("sha", None)
        if commit_sha != str(git_sha) and not self.notified:
            self.notified = True
            logger.info(
                "New update available! ({} -> {})".format(
                    str(git_sha)[:6],
                    commit_sha[:6]
                )
            )