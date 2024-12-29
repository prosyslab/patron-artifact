import datetime

logger = None
ALL = 2
ERROR = -1
INFO = 0
WARNING = 1
LOG_MODE = 0

def log(code: int, msg: str):
    if code == ERROR:
        logger.error(msg)
        print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}][ERROR] {msg}")
    elif code == INFO:
        logger.info(msg)
    elif code == WARNING:
        logger.warning(msg)
    elif code == ALL:
        logger.info(msg)
        print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}][ALL] {msg}")
    else:
        logger.debug(msg)
