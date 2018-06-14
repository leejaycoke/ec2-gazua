# -*- coding: utf-8 -*-

import ec2

import mock

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

mock_config = {'aws': mock_config_content}


@mock.patch('ec2.read_config_files', return_value=mock_config)
def test_config(mocked_read_config_files):
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


@mock.patch('ec2.read_config_files', return_value=mock_config)
@mock.patch('ec2.get_describe_instances', return_value=describe_instances)
def test_config(mocked_config_contents, mocked_instances):
    instances = ec2.get_instances()
    assert instances['aws']['hogroup'][0]['id'] == 'i-hodolman'
    assert instances['aws']['hogroup'][0]['group'] == 'hogroup'
    assert instances['aws']['hogroup'][0]['name'] == 'honame'
    assert instances['aws']['hogroup'][0]['is_running'] == True
    assert instances['aws']['hogroup'][0]['private_ip'] == '123.123.123.123'
    assert instances['aws']['hogroup'][0]['public_ip'] == '222.222.222.222'
    assert instances['aws']['hogroup'][0]['key_name'] == 'hodolkey'
    assert instances['aws']['hogroup'][0]['key_file'] == None
    assert instances['aws']['hogroup'][0]['user'] == 'ec2-user'


describe_instances_unsorted = {
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
                    {'Key': 'Name', 'Value': 'z'},
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
                    {'Key': 'Name', 'Value': '1'},
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
                    {'Key': 'Name', 'Value': '1'},
                    {'Key': 'Group', 'Value': 'aogroup'},
                ]
            }],
        },
    ]
}


@mock.patch('ec2.read_config_files', return_value=mock_config)
@mock.patch('ec2.get_describe_instances', return_value=describe_instances_unsorted)
def test_sorting(mocked_config_contents, mocked_instances):
    instances = ec2.get_instances()
    assert set([g for g in instances['aws'].keys()]) == {'aogroup', 'hogroup'}
    assert [n['name'] for n in instances['aws']['hogroup']] == ['1', 'a', 'b', 'z']
