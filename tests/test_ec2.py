# -*- coding: utf-8 -*-

from ec2gazua.ec2 import EC2Instance


def test_ec2_instance_tags():
    tags = {'Tags': [{'Key': 'InstanceId', 'Value': 'asdf'}]}
    instance = EC2Instance({}, tags)
    assert instance.tags == {'InstanceId': 'asdf'}


def test_ec2_instance_id():
    instance = EC2Instance({}, {'InstanceId': 'foo'})
    assert instance.id == 'foo'


def test_ec2_instance_name():
    tags = {'Tags': [{'Key': 'Name', 'Value': 'my-good-instance'}]}
    instance = EC2Instance({'name-tag': 'Name'}, tags)
    assert instance.name == 'my-good-instance'


def test_ec2_instance_default_name():
    instance = EC2Instance({'name-tag': 'Name'}, {})
    assert instance.name == EC2Instance.DEFAULT_NAME


def test_ec2_instance_group():
    tags = {'Tags': [{'Key': 'Team', 'Value': 'my-team'}]}
    instance = EC2Instance({'group-tag': 'Team'}, tags)
    assert instance.group == 'my-team'


def test_ec2_instance_default_group():
    instance = EC2Instance({'group-tag': 'Team'}, {})
    assert instance.group == EC2Instance.DEFAULT_GROUP


def test_ec2_instance_type():
    instance = EC2Instance({}, {'InstanceType': 't2.micro'})
    assert instance.type == 't2.micro'


def test_ec2_instance_key_name():
    instance = EC2Instance({'key-file': {'default': 'auto'}},
                           {'KeyName': 'super-secret.pem'})
    assert instance.key_name == 'super-secret.pem'


def test_ec2_instance_key_name_specified_filename():
    instance = EC2Instance({'key-file': {'default': 'hodolman.pem'}},
                           {'KeyName': 'super-secret.pem'})
    assert instance.key_name == 'hodolman.pem'


def test_ec2_instance_key_name_override_grouptag():
    instance = EC2Instance(
        {
            'group-tag': 'Team',
            'key-file':
                {
                    'default': 'auto',
                    'group': {'ho': 'high-secret.pem'}
                },
        },
        {
            'KeyName': 'super-secret.pem',
            'Tags': [{'Key': 'Team', 'Value': 'ho'}]
        }
    )
    assert instance.key_name == 'high-secret.pem'


def test_ec2_instance_key_name_override_nametag():
    instance = EC2Instance(
        {
            'name-tag': 'Name',
            'key-file':
                {
                    'default': 'auto',
                    'name': {'ins': 'high-secret.pem'}
                },
        },
        {
            'KeyName': 'super-secret.pem',
            'Tags': [{'Key': 'Name', 'Value': 'my-instance'}]
        }
    )
    assert instance.key_name == 'high-secret.pem'


def test_ec2_instance_key_file_follow_key_name():
    instance = EC2Instance(
        {
            'key-file': {'default': 'hodolman.pem'},
            'ssh-path': '~/.ssh/'
        },
        {
            'KeyName': 'super-secret.pem'
        }
    )
    assert instance.key_file == '~/.ssh/hodolman.pem'


def test_ec2_instance_private_ip():
    instance = EC2Instance(
        {},
        {
            'PrivateIpAddress': '123.123.123.123'
        }
    )
    assert instance.private_ip == '123.123.123.123'


def test_ec2_instance_public_ip():
    instance = EC2Instance(
        {},
        {
            'PublicIpAddress': '123.123.123.123'
        }
    )
    assert instance.public_ip == '123.123.123.123'


def test_ec2_instance_connect_ip_when_speicifed_private():
    instance = EC2Instance(
        {
            'connect-ip': {'default': 'private'}
        },
        {
            'PrivateIpAddress': '111.111.111.111',
            'PublicIpAddress': '123.123.123.123'
        }
    )
    assert instance.connect_ip == '111.111.111.111'


def test_ec2_instance_connect_ip_when_speicifed_public():
    instance = EC2Instance(
        {
            'connect-ip': {'default': 'public'}
        },
        {
            'PrivateIpAddress': '111.111.111.111',
            'PublicIpAddress': '123.123.123.123'
        }
    )
    assert instance.connect_ip == '123.123.123.123'


def test_ec2_instance_connect_ip_override_grouptag():
    instance = EC2Instance(
        {
            'group-tag': 'Team',
            'connect-ip': {
                'default': 'public',
                'group': {'ho': 'private'}
            }
        },
        {
            'PrivateIpAddress': '111.111.111.111',
            'PublicIpAddress': '123.123.123.123',
            'Tags': [{'Key': 'Team', 'Value': 'ho'}]
        }
    )
    assert instance.connect_ip == '111.111.111.111'


def test_ec2_instance_connect_ip_override_nametag():
    instance = EC2Instance(
        {
            'group-tag': 'Name',
            'connect-ip': {
                'default': 'public',
                'group': {'my': 'private'}
            }
        },
        {
            'PrivateIpAddress': '111.111.111.111',
            'PublicIpAddress': '123.123.123.123',
            'Tags': [{'Key': 'Name', 'Value': 'my-instance'}]
        }
    )
    assert instance.connect_ip == '111.111.111.111'


def test_ec2_instance_user():
    instance = EC2Instance(
        {'user': {'default': 'ec2-user'}},
        {}
    )
    assert instance.user == 'ec2-user'


def test_ec2_instance_override_grouptag():
    instance = EC2Instance(
        {
            'group-tag': 'Team',
            'user': {
                'default': 'ec2-user',
                'group': {'ho': 'centos'}
            }
        },
        {
            'Tags': [{'Key': 'Team', 'Value': 'ho'}]
        }
    )
    assert instance.user == 'centos'


def test_ec2_instance_override_nametag():
    instance = EC2Instance(
        {
            'name-tag': 'Name',
            'user': {
                'default': 'ec2-user',
                'name': {'man': 'centos'}
            }
        },
        {
            'Tags': [{'Key': 'Name', 'Value': 'hodolman'}]
        }
    )
    assert instance.user == 'centos'
