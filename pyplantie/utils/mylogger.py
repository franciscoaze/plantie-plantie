import logging


def new_logger(name: str, level: int = logging.INFO, extra_handlers: list = []):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    log_handler = logging.StreamHandler()
    log_handler.setLevel(level)
    formatter = logging.Formatter('%(asctime)s [%(name)s]: %(message)s')
    log_handler.setFormatter(formatter)
    logger.addHandler(log_handler)
    for handler in extra_handlers:
        logging.getLogger(handler).addHandler(log_handler)
    return logger
