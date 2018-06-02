import os
import logging
import logging.handlers

GZ_ENV = 'GZ_ENV'
ENV_LOCAL = 'LOCAL'

LOGGER_NAME = 'gz-logger'
FOLDER = os.getcwd() + '/log/'
FILENAME = 'gz.log'
LOG_FORMAT = "[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)s] %(message)s"


def get_log_path():
    if not os.path.isdir(FOLDER):
        os.makedirs(FOLDER)
    return FOLDER + FILENAME


def get_log_level():
    return logging.DEBUG if os.environ.get(GZ_ENV) == ENV_LOCAL \
        else logging.INFO


def create_logger():
    log = logging.getLogger(LOGGER_NAME)
    fomatter = logging.Formatter(LOG_FORMAT)

    file_handler = logging.FileHandler(get_log_path())
    file_handler.setFormatter(fomatter)

    log.addHandler(file_handler)
    log.setLevel(get_log_level())

    return log


log = create_logger()
