# -*- coding: utf-8 -*-

import os

import json
import yaml

from .utils import join_path

config_path = join_path(__file__, '../conf/cache.yml')

cache_folder = join_path(__file__, 'cache')
if not os.path.exists(cache_folder):
    os.mkdir(cache_folder)

count_file = join_path(__file__, 'cache/ec2-count')
if not os.path.isfile(count_file):
    with open(count_file, 'w') as fp:
        fp.write('0')

instance_file = join_path(__file__, 'cache/ec2-instances')
if not os.path.isfile(instance_file):
    with open(instance_file, 'w') as fp:
        fp.write('')


def get_config():
    with open(config_path) as fp:
        return yaml.load(fp.read())


def reset_count():
    with open(count_file, 'w') as fp:
        fp.write('0')


def get_count():
    with open(count_file) as fp:
        return int(fp.read())


def _write_count(count):
    with open(count_file, 'w') as fp:
        fp.write(str(count))


def increase_count():
    increased_count = get_count() + 1
    _write_count(increased_count)


def put_instances(instances):
    json_instances = json.dumps(instances)
    with open(instance_file, 'w') as fp:
        fp.write(json_instances)


def get_instances():
    with open(instance_file) as fp:
        return json.loads(fp.read())


def has_instances():
    with open(instance_file) as fp:
        return fp.read().strip() != ''
