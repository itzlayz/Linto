# █ ▀█▀ ▀█ █   ▄▀█ █▄█ ▀█
# █ ░█░ █▄ █▄▄ █▀█ ░█░ █▄
# https://t.me/itzlayz
#                           
# 🔒 Licensed under the GNU AGPLv3
# https://www.gnu.org/licenses/agpl-3.0.html

import logging

def init():
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)

    fileHandler = logging.FileHandler("linto.log", "w")

    fmt = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        '%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(fmt)
    fileHandler.setFormatter(fmt)

    logger = logging.getLogger()
    logger.addHandler(handler)
    logger.addHandler(fileHandler)
    logger.setLevel(logging.DEBUG)

    logging.getLogger("asyncio").setLevel(logging.WARNING)
    logging.getLogger("aiohttp").setLevel(logging.WARNING)
    logging.getLogger("discord").setLevel(logging.ERROR)
    logging.getLogger("git").setLevel(logging.WARNING)

    logging.getLogger("flet_core").setLevel(logging.FATAL)
    logging.getLogger("flet_runtime").setLevel(logging.FATAL)

    return logger