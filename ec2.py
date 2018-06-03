# -*- coding: utf-8 -*-


from os import listdir
from os.path import dirname
from os.path import join
from os.path import realpath

import boto3
import yaml


def get_config_files():
    folder = join(dirname(realpath(__file__)), 'conf')
    return [join(folder, f) for f in listdir(folder)]


def read_config_files():
    contents = []
    for config_file in get_config_files():
        with open(config_file) as fp:
            contents.append(fp.read())
    return contents


def get_configs():
    contents = read_config_files()
    configs = {}

    for content in contents:
        config = yaml.load(content)
        configs[config['name']] = config

    return configs


def create_connection(access_key_id, secret_access_key, region):
    session = boto3.session.Session(
        aws_access_key_id=access_key_id,
        aws_secret_access_key=secret_access_key,
        region_name=region)
    return session.client('ec2')


def get_describe_instances(config):
    args = [config['credential']['aws_access_key_id'],
            config['credential']['aws_secret_access_key'],
            config['credential']['region']]
    client = create_connection(*args)
    return client.describe_instances()


def clear_instance(i, group_tag, name_tag):
    tags = {t['Key']: t['Value'] for t in i.get('Tags', [])}

    instance = {
        'id': i['InstanceId'],
        'name': tags.get(name_tag, 'unknown_name'),
        'group': tags.get(group_tag, 'unknown_group'),
        'type': i['InstanceType'],
        'key_name': i.get('KeyName', '-'),
        'private_ip': i.get('PrivateIpAddress', '-'),
        'public_ip': i.get('PublicIpAddress', '-'),
        'is_running': i['State']['Name'] == 'running',
        'tags': tags,
    }

    return instance


def get_instances():
    configs = get_configs()
    instances = {}

    for name, config in configs.items():
        instances[name] = {}

        print 'Get instances from ec2 [%s]' % name
        resp = get_describe_instances(config)

        if len(resp['Reservations']) == 0:
            continue

        cleared_instances = [clear_instance(i['Instances'][0],
                                           config['tag']['group'],
                                           config['tag']['name']) \
                            for i in resp['Reservations']]

        for i in cleared_instances:
            group = i['group']

            if i['group'] not in instances[name]:
                instances[name][group] = []

            instances[name][group].append(i)

    return instances
