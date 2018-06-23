# -*- coding: utf-8 -*-

from os.path import dirname
from os.path import join
from os.path import realpath


def join_path(file, path):
    return join(dirname(realpath(file)), path)
