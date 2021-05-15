# -*- coding: utf-8 -*-

import yaml

from os import path

from ec2gazua.utils import read


class Config(object):
    CONFIG_PATH = path.expanduser('~')
    FILENAME = '.ec2-gz'
    CONFIG_FILE = CONFIG_PATH + '/' + FILENAME

    _items = {}

    def __init__(self):
        self._valid_config_file()
        self._load()

    def _valid_config_file(self):
        if not path.exists(self.CONFIG_FILE):
            raise IOError("Config file not exists: %s" % self.CONFIG_FILE)

        if not path.isfile(self.CONFIG_FILE):
            raise IOError(
                ".ec2-gz must be a file. not directory: %s" % self.CONFIG_FILE)

    def _load(self):
        content = self._read()

        configs = {}

        for data in yaml.safe_load_all(content):
            if data['name'] in configs:
                raise ValueError(
                    '%s is duplicated name in config' % data['name'])
            configs[data['name']] = data

        self._items = configs

    def items(self):
        return self._items.items()

    def _read(self):
        return read(self.CONFIG_FILE)

    def __getitem__(self, aws_name):
        return self._items[aws_name]
