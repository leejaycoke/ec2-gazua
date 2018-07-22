# -*- coding: utf-8 -*-

from os.path import dirname
from os.path import join
from os.path import realpath
from os.path import isfile


def join_path(file, path):
    return join(dirname(realpath(file)), path)


def read(file):
    with open(file) as fp:
        return fp.read()
