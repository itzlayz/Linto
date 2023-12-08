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

    return logger