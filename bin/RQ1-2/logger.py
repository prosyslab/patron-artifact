import datetime
import config
logger = None

ERROR = -1
INFO = 0
WARNING = 1


def openings():
    if config.configuration["args"].skip_intro:
        return
    print('______  ___ ___________ _____ _   _ ')
    print('| ___ \/ _ \_   _| ___ \  _  | \ | |')
    print('| |_/ / /_\ \| | | |_/ / | | |  \| |')
    print('|  __/|  _  || | |    /| | | | . ` |')
    print('| |   | | | || | | |\  \\ \_/ / |\  |')
    print('\_|   \_| |_/\_/ \_| \_|\___/\_| \_/\n')
    print('                             v.0.1.0')
    print('                by prosys lab, KAIST\n')
    print('YOU ARE RUNNING THE REPRODUCTION FOR RQ1 and 2 EXPERIMENT\n')


def log(code: int, msg: str):
    if code == ERROR:
        logger.error(msg)
    elif code == INFO:
        logger.info(msg)
    elif code == WARNING:
        logger.warning(msg)
    else:
        logger.debug(msg)
