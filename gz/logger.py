# -*- coding: utf-8 -*-

import sys
import os
import logging
import logging.handlers

from . import utils


class FileLogger(object):
    NAME = 'file_logger'

    LOG_FOLDER = utils.join_path(__file__, '../log')
    LOG_FILE = LOG_FOLDER + '/gz.log'

    LOG_LEVEL = {
        None: logging.INFO,
        'DEV': logging.DEBUG,
    }.get(os.environ.get('GZ_ENV'), logging.DEBUG)

    LOG_FORMAT = "[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)s] %(" \
                 "message)s "

    def create(self):
        self._create_folder()
        logger = logging.getLogger(self.NAME)
        fomatter = logging.Formatter(self.LOG_FORMAT)

        file_handler = logging.FileHandler(self.LOG_FILE)
        file_handler.setFormatter(fomatter)

        logger.addHandler(file_handler)
        logger.setLevel(self.LOG_LEVEL)
        return logger

    def _create_folder(self):
        if not os.path.exists(self.LOG_FOLDER):
            os.makedirs(self.LOG_FOLDER)


class ConsoleLogger(object):
    NAME = 'stream_logger'

    def __init__(self):
        self.logger = self._create()

    def _create(self):
        logger = logging.getLogger(self.NAME)
        logger.setLevel(logging.INFO)

        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setLevel(logging.INFO)
        logger.addHandler(stream_handler)
        return logger

    def console(self, message):
        self.logger.info(message)


log = FileLogger().create()

console = ConsoleLogger().console
