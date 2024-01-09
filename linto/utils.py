# █ ▀█▀ ▀█ █   ▄▀█ █▄█ ▀█
# █ ░█░ █▄ █▄▄ █▀█ ░█░ █▄
# https://t.me/itzlayz
#                           
# 🔒 Licensed under the GNU AGPLv3
# https://www.gnu.org/licenses/agpl-3.0.html

import os
import ast
import types
import typing
import asyncio
import string
import random
import atexit
import logging

from contextlib import suppress
from . import version

try:
    import git
    git_sha = git.Repo().head.commit.hexsha
except:
    logging.exception("Git error, look for git in path")

logger = logging.getLogger()
LETTERS = string.ascii_uppercase + string.ascii_lowercase + "".join(
    str(i) for i in range(1, 10))

def insert_returns(body):
    if isinstance(body[-1], ast.Expr):
        body[-1] = ast.Return(body[-1].value)
        ast.fix_missing_locations(body[-1])
        if isinstance(body[-1], ast.If):
            insert_returns(body[-1].body)
            insert_returns(body[-1].orelse)
        if isinstance(body[-1], ast.With):
            insert_returns(body[-1].body)

async def epc(code, env=None):
    """
    Evaluate python code
    :param code: python code
    :param env: code globals
    :return: Output/Error no raise
    """
    if env is None:
        env = {}
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
    
def suppress_exc(
    func: types.FunctionType, 
    exception: Exception = Exception,
    coro_callback: types.FunctionType = None
) -> typing.Any:
    """
    Supress function's exception
    Supports asynchronous functions

    :param func: Function to do
    :param exception: Exception to supress (optional
                      do not specify to supress all exceptions)
    :return: Function output 
    """
    funcs = (types.FunctionType, types.LambdaType)

    if not isinstance(func, funcs):
        raise ValueError("Invalid type of function")
    
    if asyncio.iscoroutinefunction(func):
        if not coro_callback:
            raise ValueError(
                "coro_callback is required for asynchronous functions")
        
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.get_event_loop()

        task = loop.create_task(func())
        task.add_done_callback(lambda _: coro_callback(task.result()))

        loop.run_until_complete(task)
        return task.result()
    
    with suppress(exception):
        return func()

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
    except:  # noqa: E722
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
    except:  # noqa: E722
        return 0
    
def _atexit(func, *args, **kwargs):
    """
    Register func at exit
    :param func: Function to do on exit
    :return: func
    """
    return atexit.register(func, *args, **kwargs)


def rand(length: int = 10) -> str:
    """
    Generate random string
    :param length: String length
    :return: Random string
    """
    return "".join(
        random.choice(
            LETTERS) for _ in range(length)
    )

def git_diff():
    try:
        import git
        
        repo = git.Repo()
        diff = repo.git.log([f"HEAD..origin/{version.branch}", "--oneline"])

        return diff
    except:
        logging.exception("Git error, look for git in path")

async def check_output(command: str) -> asyncio.subprocess.Process:
    proc = await asyncio.create_subprocess_exec(
        command.strip(), 
        stdin=asyncio.subprocess.STDOUT,
        stderr=asyncio.subprocess.STDOUT,
        stdout=asyncio.subprocess.STDOUT
    )

    return proc

def iniFormatting(text: str):
    return "```ini\n[ " + text + " ]\n```"