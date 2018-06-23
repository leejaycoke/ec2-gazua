# -*- coding: utf-8 -*-

from ec2gazua import ec2
from ec2gazua import cache

mock_config_content = """
ssh-path: /path/to

credential:
    aws_access_key_id: XXX1
    aws_secret_access_key: XXX2
    region: ap-northeast-2

group-tag: Group
name-tag: Name

connect-ip:
    default: public
    group:
      test1: private
    name:
      test2: public

key-file:
    default: auto
    group:
        test1: test_rsa1
    name:
        test2: test_rsa2

user:
    default: ec2-user
    group:
        test1: centos
    name:
        test2: leejuhyun

"""


def test_get_configs(monkeypatch):
    def read_config_files():
        return {'aws': mock_config_content}

    monkeypatch.setattr(ec2, 'read_config_files', read_config_files)
    configs = ec2.get_configs()

    assert configs['aws']['credential']['aws_access_key_id'] == 'XXX1'
    assert configs['aws']['credential']['aws_secret_access_key'] == 'XXX2'
    assert configs['aws']['credential']['region'] == 'ap-northeast-2'

    assert configs['aws']['group-tag'] == 'Group'
    assert configs['aws']['name-tag'] == 'Name'

    assert configs['aws']['connect-ip']['default'] == 'public'
    assert configs['aws']['connect-ip']['group']['test1'] == 'private'
    assert configs['aws']['connect-ip']['name']['test2'] == 'public'

    assert configs['aws']['key-file']['default'] == 'auto'
    assert configs['aws']['key-file']['group']['test1'] == 'test_rsa1'
    assert configs['aws']['key-file']['name']['test2'] == 'test_rsa2'

    assert configs['aws']['user']['default'] == 'ec2-user'
    assert configs['aws']['user']['group']['test1'] == 'centos'
    assert configs['aws']['user']['name']['test2'] == 'leejuhyun'


describe_instances = {
    'Reservations': [
        {'Instances': [
            {
                'InstanceId': 'i-hodolman',
                'InstanceType': 't2.micro',
                'State': {
                    'Name': 'running',
                },
                'PrivateIpAddress': '123.123.123.123',
                'PublicIpAddress': '222.222.222.222',
                'KeyName': 'hodolkey',
                'Tags': [
                    {'Key': 'Group', 'Value': 'hogroup'},
                    {'Key': 'Name', 'Value': 'honame'}
                ]
            }
        ]}
    ]
}


def test_config(monkeypatch):
    def read_config_files():
        return {'aws': mock_config_content}

    def get_describe_instances(_):
        return describe_instances

    monkeypatch.setattr(ec2, 'read_config_files', read_config_files)
    monkeypatch.setattr(ec2, 'get_describe_instances', get_describe_instances)

    instances = ec2.get_instances()
    assert instances['aws']['hogroup'][0]['id'] == 'i-hodolman'
    assert instances['aws']['hogroup'][0]['group'] == 'hogroup'
    assert instances['aws']['hogroup'][0]['name'] == 'honame'
    assert instances['aws']['hogroup'][0]['is_running'] is True
    assert instances['aws']['hogroup'][0]['private_ip'] == '123.123.123.123'
    assert instances['aws']['hogroup'][0]['public_ip'] == '222.222.222.222'
    assert instances['aws']['hogroup'][0]['key_name'] == 'hodolkey'
    assert instances['aws']['hogroup'][0]['key_file'] is None
    assert instances['aws']['hogroup'][0]['user'] == 'ec2-user'


describe_instances_unsorted = {
    'Reservations': [
        {'Instances': [
            {
                'InstanceId': 'i-hodolman',
                'InstanceType': 't2.micro',
                'State': {
                    'Name': 'terminated',
                },
                'PrivateIpAddress': '123.123.123.123',
                'PublicIpAddress': '222.222.222.222',
                'KeyName': 'hodolkey',
                'Tags': [
                    {'Key': 'Name', 'Value': 'a'},
                    {'Key': 'Group', 'Value': 'hogroup'},
                ]
            }],
        },
        {'Instances': [
            {
                'InstanceId': 'i-hodolman',
                'InstanceType': 't2.micro',
                'State': {
                    'Name': 'running',
                },
                'PrivateIpAddress': '123.123.123.123',
                'PublicIpAddress': '222.222.222.222',
                'KeyName': 'hodolkey',
                'Tags': [
                    {'Key': 'Name', 'Value': 'b'},
                    {'Key': 'Group', 'Value': 'hogroup'},
                ]
            }],
        },
        {'Instances': [
            {
                'InstanceId': 'i-hodolman',
                'InstanceType': 't2.micro',
                'State': {
                    'Name': 'running',
                },
                'PrivateIpAddress': '123.123.123.123',
                'PublicIpAddress': '222.222.222.222',
                'KeyName': 'hodolkey',
                'Tags': [
                    {'Key': 'Name', 'Value': 'c'},
                    {'Key': 'Group', 'Value': 'hogroup'},
                ]
            }],
        },
        {'Instances': [
            {
                'InstanceId': 'i-hodolman',
                'InstanceType': 't2.micro',
                'State': {
                    'Name': 'terminated',
                },
                'PrivateIpAddress': '123.123.123.123',
                'PublicIpAddress': '222.222.222.222',
                'KeyName': 'hodolkey',
                'Tags': [
                    {'Key': 'Name', 'Value': 'd'},
                    {'Key': 'Group', 'Value': 'hogroup'},
                ]
            }],
        },
        {'Instances': [
            {
                'InstanceId': 'i-hodolman',
                'InstanceType': 't2.micro',
                'State': {
                    'Name': 'running',
                },
                'PrivateIpAddress': '123.123.123.123',
                'PublicIpAddress': '222.222.222.222',
                'KeyName': 'hodolkey',
                'Tags': [
                    {'Key': 'Name', 'Value': 'e'},
                    {'Key': 'Group', 'Value': 'aogroup'},
                ]
            }],
        },
    ]
}


def test_sorting(monkeypatch):
    def read_config_files():
        return {'aws': mock_config_content}

    def get_describe_instances(_):
        return describe_instances_unsorted

    def get_count():
        return 10

    def put_instances(_):
        pass

    def reset_count():
        pass

    monkeypatch.setattr(ec2, 'read_config_files', read_config_files)
    monkeypatch.setattr(ec2, 'get_describe_instances', get_describe_instances)
    monkeypatch.setattr(cache, 'get_count', get_count)
    monkeypatch.setattr(cache, 'put_instances', put_instances)
    monkeypatch.setattr(cache, 'reset_count', reset_count)

    instances = ec2.get_instances()
    assert set([g for g in instances['aws'].keys()]) == {'aogroup', 'hogroup'}
    assert [n['name'] for n in instances['aws']['hogroup']] == ['b', 'c',
                                                                'a', 'd']
