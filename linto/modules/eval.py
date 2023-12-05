import ast

from discord.ext import commands

def insert_returns(body):
    if isinstance(body[-1], ast.Expr):
        body[-1] = ast.Return(body[-1].value)
        ast.fix_missing_locations(body[-1])
        if isinstance(body[-1], ast.If):
            insert_returns(body[-1].body)
            insert_returns(body[-1].orelse)
        if isinstance(body[-1], ast.With):
            insert_returns(body[-1].body)

async def epc(code, env={}):
    try:
        fn_name = "_eval_expr"
        cmd = "\n".join(f" {i}" for i in code.splitlines())
        body = f"async def {fn_name}():\n{cmd}"
        parsed = ast.parse(body)
        body = parsed.body[0].body
        insert_returns(body)
        env = {'__import__': __import__, **env}
        exec(compile(parsed, filename="<ast>", mode="exec"), env)
        return (await eval(f"{fn_name}()", env))
    except Exception as error:
        return error

class Eval(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
    
    @commands.command()
    async def eval(self, ctx, *, code: str):
        output = await epc(
            code,
            {
                "self": self,
                "bot": self.bot,
                "ctx": ctx
            }
        )
        await ctx.reply(f"```py\n{output}\n```")

async def setup(bot):
    await bot.add_cog(Eval(bot))