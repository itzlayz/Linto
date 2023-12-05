import logging

def init():
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)

    fmt = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        '%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(fmt)

    logger = logging.getLogger()
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    logging.getLogger("asyncio").setLevel(logging.WARNING)
    logging.getLogger("discord").setLevel(logging.WARNING)

    return logger