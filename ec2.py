# -*- coding: utf-8 -*-


from os import listdir
from os.path import isfile
from os.path import dirname
from os.path import join
from os.path import realpath
from os.path import expanduser
from logger import log

import boto3
import yaml


def get_config_files():
    folder = join(dirname(realpath(__file__)), 'conf')
    return [join(folder, f) for f in listdir(folder) if f.endswith(".yml")]


def read_config_files():
    contents = {}
    for config_file in get_config_files():
        aws_name = config_file.rsplit('/', 1)[1].rsplit('.', 1)[0]  # /path/conf/aws.yml -> aws
        with open(config_file) as fp:
            contents[aws_name] = fp.read()
    return contents


def get_configs():
    contents = read_config_files()
    configs = {}

    for aws_name, content in contents.items():
        configs[aws_name] = yaml.load(content)
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


def get_key_file(filename):
    filepath = expanduser(filename)
    if isfile(filepath):
        return filepath
    elif isfile(filepath + '.pem'):
        return filepath + '.pem'
    else:
        return None


def override_ip(instance, config):
    for group_name, ip_type in config.get('group', {}).items():
        if group_name in instance['group']:
            instance['connect_ip'] = ip_type

    for group_name, ip_type in config.get('name', {}).items():
        if group_name in instance['name']:
            instance['connect_ip'] = ip_type

    return instance


def override_key_file(instance, ssh_path, config):
    for group_name, key_file in config.get('group', {}).items():
        if group_name in instance['group']:
            instance['key_file'] = ssh_path + key_file
            instance['key_name'] = key_file

    for group_name, key_file in config.get('name', {}).items():
        if group_name in instance['name']:
            instance['key_file'] = ssh_path + key_file
            instance['key_name'] = key_file

    return instance


def override_user(instance, config):
    for group_name, user in config.get('group', {}).items():
        if group_name in instance['group']:
            instance['user'] = user

    for group_name, user in config.get('name', {}).items():
        if group_name in instance['name']:
            instance['user'] = user

    return instance


def clear_tags(tags):
    return {t['Key']: t['Value'] if t['Value'] != '' else None for t in tags}


def clear_instance(instance, config):
    tags = clear_tags(instance.get('Tags', []))

    instance = {
        'id': instance['InstanceId'],
        'name': tags.get(config['name-tag'], '!-UNKNOWN_NAME'),
        'group': tags.get(config['group-tag'], '!-UNKNOWN_GROUP'),
        'type': instance['InstanceType'],
        'key_name': instance.get('KeyName', '?'),
        'private_ip': instance.get('PrivateIpAddress', '?'),
        'public_ip': instance.get('PublicIpAddress', '?'),
        'is_running': instance['State']['Name'] == 'running',
        'tags': tags,
        'user': config['user']['default']
    }

    instance['connect_ip'] = instance['private_ip'] if config['connect-ip']['default'] == 'private' \
        else instance['public_ip']

    if config['key-file']['default'] == 'auto':
        instance['key_file'] = get_key_file(config['ssh-path'] + '/' + instance['key_name'])
    else:
        instance['key_file'] = config['ssh-path'] + '/' + config['key-file']['default']

    instance = override_ip(instance, config['connect-ip'])
    instance = override_key_file(instance, config['ssh-path'], config['key-file'])
    instance = override_user(instance, config['user'])

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

        cleared_instances = [clear_instance(i['Instances'][0], config) \
                             for i in resp['Reservations']]

        for i in cleared_instances:
            group = i['group']

            if i['group'] not in instances[name]:
                instances[name][group] = []

            instances[name][group].append(i)

    return instances
