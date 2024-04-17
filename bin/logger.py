import datetime

logger = None

ERROR = -1
INFO = 0
WARNING = 1

def log(code: int, msg: str):
    if code == ERROR:
        logger.error(msg)
    elif code == INFO:
        logger.info(msg)
    elif code == WARNING:
        logger.warning(msg)
    else:
        logger.debug(msg)
