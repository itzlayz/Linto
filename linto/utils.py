import os
import ast
import logging
from discord.ext import commands

logger = logging.getLogger()
async def load_extensions(bot: commands.Bot, reload: bool = False):
    for module in os.listdir("linto/modules"):
        if module.endswith(".py"):
            try:
                await bot.load_extension("linto.modules." + module[:-3])
            except commands.errors.ExtensionAlreadyLoaded:
                if reload:
                    await bot.unload_extension("linto.modules." + module[:-3])
                    await bot.load_extension("linto.modules." + module[:-3])

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

def get_ram() -> float:
    """
    :return: Memory usage in megabytes.
    """
    
    try:
        import psutil
        process = psutil.Process(os.getpid())
        mem = process.memory_info()[0] / 2.0**20
        for child in process.children(recursive=True):
            mem += child.memory_info()[0] / 2.0**20
        return round(mem, 1)
    except:
        return 0

def get_cpu() -> float:
    """
    :return: CPU usage as a percentage.
    """

    try:
        import psutil

        process = psutil.Process(os.getpid())
        cpu = process.cpu_percent()

        for child in process.children(recursive=True):
            cpu += child.cpu_percent()

        return cpu
    except:
        return 0