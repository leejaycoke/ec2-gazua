# -*- coding: utf-8 -*-


from os import listdir
from os.path import dirname
from os.path import join
from os.path import realpath

import boto3
import yaml

import ssh


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


def get_ec2_names():
    return get_configs().keys()


def get_instances():
    names = get_ec2_names()
    for name in names:


def get_ec2_

def create_client():
    config = get_configs()
    access_key = config['credential']['aws_access_key_id']
    secret_key = config['credential']['aws_secret_access_key']
    region = config['credential']['region']

    if access_key and secret_key:
        session = boto3.session.Session(aws_access_key_id=access_key,
                                        aws_secret_access_key=secret_key,
                                        region_name=region)
    else:
        session = boto3.session.Session()

    return session.client('ec2')


def get_describe_instances():
    client = create_client()
    ec2_list = client.describe_instances()
    return ec2_list


def get_list():
    ec2_list = get_describe_instances()
    ssh.exclude_ec2_config()

    ssh_configs = {}
    for rev in ec2_list['Reservations']:
        ssh_config = convert_to_ssh_config(rev['Instances'][0])

        if ssh_config['group'] not in ssh_configs:
            ssh_configs[ssh_config['group']] = []
        ssh_configs[ssh_config['group']].append(ssh_config)

    ec2_lines = []

    for group, config in ssh_configs.items():

        ec2_lines.append(ssh.GZ_GROUP_PREFIX + group + '\n')

        for content in config:
            ec2_lines.append('Host ' + content['name'] + '\n')
            ec2_lines.append('\tHostName ' + content['hostname'] + '\n')
            ec2_lines.append('\tUser ' + content['user'] + '\n')
            ec2_lines.append('\tIdentityFile ' +
                             content['identity_file'] + '\n\n')

    ssh.write_new_ec2_config(ec2_lines)


aws_config = get_configs()

HOSTNAME_FINDER = {
    'public_ip': lambda i: i.get('PublicIpAddress', i['PrivateIpAddress']),
    'public_dns': lambda i: i['PublicDnsName'],
    'private_ip': lambda i: i['PrivateIpAddress'],
    'private_dns': lambda i: i['PrivateDnsName'],
}


def convert_to_ssh_config(instance):
    group, name = None, None

    for tag in instance.get('Tags', []):
        if tag['Key'] == aws_config['tag']['group']:
            group = tag['Value']
        elif tag['Key'] == aws_config['tag']['name']:
            name = tag['Value']

    if not group:
        group = 'default'

    group = aws_config['group-prefix'] + ' ' + group

    if not name:
        name = instance.get('PublicIpAddress') or instance.get(
            'PrivateDnsName')

    # host
    hostname = HOSTNAME_FINDER[aws_config['hostname']['default']](instance)
    if group in aws_config['hostname']['group'].keys():
        ip_way = aws_config['hostname']['group'][group]
        hostname = HOSTNAME_FINDER[ip_way](instance)

    if name in aws_config['hostname']['name'].keys():
        ip_way = aws_config['hostname']['name'][name]
        hostname = HOSTNAME_FINDER[ip_way](instance)

    # identity-file
    identity_file = aws_config['identity-file']['default']
    if group in aws_config['identity-file']['group'].keys():
        identity_file = aws_config['identity-file']['group'][group]

    if name in aws_config['identity-file']['name'].keys():
        identity_file = aws_config['identity-file']['name'][name]

    # user
    user = aws_config['user']['default']
    if user in aws_config['user']['group'].keys():
        user = aws_config['user']['group'][user]

    if user in aws_config['user']['name'].keys():
        user = aws_config['user']['name'][user]

    return {
        'group': group,
        'name': name,
        'user': user,
        'hostname': hostname,
        'identity_file': identity_file,
    }
