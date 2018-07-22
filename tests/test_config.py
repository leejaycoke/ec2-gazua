# -*- coding: utf-8 -*-

import mock
import pytest

from ec2gazua.utils import join_path
from ec2gazua.utils import read
from ec2gazua.config import Config

config_yaml1 = read(join_path(__file__, 'resources/mock_config1.yml'))


@mock.patch('ec2gazua.config.Config._read', return_value=config_yaml1)
def test_valid_config_file(mock_read):
    config = Config()

    assert config._items['my-aws'] == {
        'name': 'my-aws',
        'credential': {
            'aws_access_key_id': 'xxx1',
            'aws_secret_access_key': 'xxx2',
            'region': 'ap-northeast-2'
        },
        'group-tag': 'Group',
        'name-tag': 'Name',
        'connect-ip': {
            'default': 'public',
            'group': {'test1': 'private'},
            'name': {'test2': 'private'}
        },
        'key-file': {
            'default': 'auto',
            'group': {'test1': 'test_rsa1'},
            'name': {'test2': 'test_rsa2'}
        },
        'user': {
            'default': 'ec2-user',
            'group': {'test1': 'centos'},
            'name': {'test2': 'leejuhyun'}
        }
    }

    assert config._items['enterprise'] == {
        'name': 'enterprise',
        'credential': {
            'aws_access_key_id': 'asd1',
            'aws_secret_access_key': 'asd2',
            'region': 'ap-northeast-2'
        }
    }

    assert mock_read.call_count == 1


config_yaml2 = read(join_path(__file__, 'resources/mock_config2.yml'))


@mock.patch('ec2gazua.config.Config._read', return_value=config_yaml2)
def test_valid_config_file(_):
    with pytest.raises(ValueError) as e:
        Config()

    assert 'my-aws is duplicated name in config' == str(e.value)
