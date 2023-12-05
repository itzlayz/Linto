from discord.ext import commands

class Info(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
    
    @commands.command()
    async def info(self, ctx):
        modules = len(self.bot.cogs)
        guilds = len((await self.bot.fetch_guilds(with_counts=False)))

        await ctx.reply(
            f"🤖 **Owner: {self.bot.user}**\n"
            f":cd: **Modules: {modules}**\n"
            f"📁 **Guilds: {guilds}**\n"
        )

async def setup(bot):
    await bot.add_cog(Info(bot))