import logging


def new_logger(name: str, level: int = logging.INFO):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    log_handler = logging.StreamHandler()
    log_handler.setLevel(level)
    formatter = logging.Formatter('%(asctime)s [%(levelname)s]: %(message)s')
    log_handler.setFormatter(formatter)
    logger.addHandler(log_handler)

    return logger
