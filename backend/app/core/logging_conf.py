import logging
from pythonjsonlogger import jsonlogger

def setup_logging() -> None:
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logHandler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter("%(asctime)s %(levelname)s %(name)s %(message)s")
    logHandler.setFormatter(formatter)
    if logger.handlers:
        logger.handlers = []
    logger.addHandler(logHandler)
