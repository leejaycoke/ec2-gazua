# -*- coding: utf-8 -*-

from logger import log
import re

import collections

from os import path
from os.path import expanduser

home = expanduser("~")


GROUP_PATTERN = re.compile('^#gz\:(group\=(?P<group_name>[^,]+))')
DEFAULT_GROUP = 'default'

EXPECTED_CONFIG_PREFIXES = [
    'Host',
    'HostName',
    'User',
    'IdentityFile',
    'Port',
]

GZ_GROUP_PREFIX = '#gz:group='

HOST = 'Host'

GZ_EC2_START = '#gz:ec2-start'
GZ_EC2_END = '#gz:ec2-end'


def get_config_file():
    filename = home + "/.ssh/config"
    if not path.isfile(filename):
        raise IOError("SSH config file not exists '%s'" % filename)
    return filename


def read_config_file():
    with open(get_config_file()) as fp:
        return fp.readlines()


def parse_group_name(line):
    match = GROUP_PATTERN.match(line)
    if match:
        return match.groupdict()['group_name']


def exclude_ec2_config():
    lines = read_config_file()

    delete_flag = False
    new_lines = []
    for line in lines:
        if not delete_flag:
            if not line.startswith(GZ_EC2_START):
                new_lines.append(line)
                continue
            delete_flag = True
        else:
            if line.startswith(GZ_EC2_END):
                delete_flag = False
    return new_lines


def remove_pre_loaded_ec2_config():
    excluded_lines = exclude_ec2_config()
    with open(get_config_file(), 'w') as fp:
        for line in excluded_lines:
            fp.write(line)


def write_new_ec2_config(lines):
    remove_pre_loaded_ec2_config()
    with open(get_config_file(), 'a') as fp:
        fp.write(GZ_EC2_START + '\n')
        for line in lines:
            fp.write(line)
        fp.write(GZ_EC2_END + '\n')


def parse_config():
    contents = [line.strip()
                for line in read_config_file() if line.strip() != '']
    current_group = DEFAULT_GROUP

    configs = collections.OrderedDict()
    configs[current_group] = collections.OrderedDict()

    current_host = None

    for line in contents:

        # if starts with #gz comments
        if line.startswith(GZ_GROUP_PREFIX):
            current_group = parse_group_name(line)
            if current_group not in configs:
                configs[current_group] = collections.OrderedDict()

        else:
            try:
                values = line.split()
                if values[0] not in EXPECTED_CONFIG_PREFIXES:
                    raise Exception("Unexpted line specified")
            except Exception as e:
                log.warning(str(e) + ", line=%s" % line)
                continue

            key = values[0]
            value = '-'.join(values[1:])

            if key == HOST:
                current_host = value
                configs[current_group][current_host] = collections.OrderedDict()
            else:
                configs[current_group][current_host][key] = value

    if len(configs[DEFAULT_GROUP]) == 0:
        del configs[DEFAULT_GROUP]

    return configs
