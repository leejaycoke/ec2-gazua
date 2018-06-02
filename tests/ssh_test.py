# -*- coding: utf-8 -*-

import ssh
import mock


@mock.patch('ssh.get_config_file', return_value='resources/ssh_config')
def test_read_config_file(mocked_get_config_file):
    ssh_lines = ssh.read_config_file()
    assert len(ssh_lines) == 4


@mock.patch('ssh.read_config_file', return_value=[
    '#gz:group=mygroup',
    'Host live-was',
    'HostName 123.123.123.1',
    'User testuser',
    'Port 2222',
    'IdentityFile /home/ssh/path',
])
def test_parse_config(mocked_read_config_file):
    configs = ssh.parse_config()
    assert ssh.DEFAULT_GROUP not in configs
    assert 'mygroup' in configs
    assert 'live-was' in configs['mygroup']
    assert configs['mygroup']['live-was']['User'] == 'testuser'
    assert configs['mygroup']['live-was']['Port'] == '2222'
    assert configs['mygroup']['live-was']['IdentityFile'] == '/home/ssh/path'


@mock.patch('ssh.read_config_file', return_value=[
    '#gz:group=mygroup',
    'Host was1',
    'HostName 123.123.123.1',
    'User user1',
    'Port 1',
    'IdentityFile /home/.ssh/id_rsa1',
    'Host was2',
    'HostName 123.123.123.2',
    'User user2',
    'Port 2',
    'IdentityFile /home/.ssh/id_rsa2',
])
def test_parse_config_list(mocked_read_config_file):
    configs = ssh.parse_config()
    assert ssh.DEFAULT_GROUP not in configs
    assert 'mygroup' in configs
    assert 'was1' in configs['mygroup']
    assert configs['mygroup']['was1']['User'] == 'user1'
    assert configs['mygroup']['was1']['Port'] == '1'
    assert configs['mygroup']['was1']['IdentityFile'] == '/home/.ssh/id_rsa1'

    assert 'was2' in configs['mygroup']
    assert configs['mygroup']['was2']['User'] == 'user2'
    assert configs['mygroup']['was2']['Port'] == '2'
    assert configs['mygroup']['was2']['IdentityFile'] == '/home/.ssh/id_rsa2'


@mock.patch('ssh.read_config_file', return_value=[
    '#gz:group=mygroup1',
    'Host was1',
    'HostName 123.123.123.1',
    'User user1',
    'Port 1',
    'IdentityFile /home/.ssh/id_rsa1',
    '#gz:group=mygroup2',
    'Host was2',
    'HostName 123.123.123.2',
    'User user2',
    'Port 2',
    'IdentityFile /home/.ssh/id_rsa2',
])
def test_parse_config_multi_group(mocked_read_config_file):
    configs = ssh.parse_config()
    assert ssh.DEFAULT_GROUP not in configs
    assert 'mygroup1' in configs
    assert 'was1' in configs['mygroup1']
    assert configs['mygroup1']['was1']['User'] == 'user1'
    assert configs['mygroup1']['was1']['Port'] == '1'
    assert configs['mygroup1']['was1']['IdentityFile'] == '/home/.ssh/id_rsa1'

    assert 'mygroup2' in configs
    assert 'was2' in configs['mygroup2']
    assert configs['mygroup2']['was2']['User'] == 'user2'
    assert configs['mygroup2']['was2']['Port'] == '2'
    assert configs['mygroup2']['was2']['IdentityFile'] == '/home/.ssh/id_rsa2'


@mock.patch('ssh.read_config_file', return_value=[
    '#gz:ec2-start',
    '1',
    '2',
    '#gz:ec2-end'
])
def test_exclude_ec2_config_all_lines(mocked_read_config_file):
    new_lines = ssh.exclude_ec2_config()
    assert len(new_lines) == 0


@mock.patch('ssh.read_config_file', return_value=[
    '#gz:ec2-start',
    '1',
    '#gz:ec2-end',
    '2',
    '3'
])
def test_exclude_ec2_config_top_line(mocked_read_config_file):
    new_lines = ssh.exclude_ec2_config()
    assert len(new_lines) == 2
    assert new_lines[0] == '2'
    assert new_lines[1] == '3'


@mock.patch('ssh.read_config_file', return_value=[
    '1',
    '#gz:ec2-start',
    '2',
    '#gz:ec2-end'
])
def test_exclude_ec2_config_last_line(mocked_read_config_file):
    new_lines = ssh.exclude_ec2_config()
    assert len(new_lines) == 1
    assert new_lines[0] == '1'


@mock.patch('ssh.read_config_file', return_value=[
    '1',
    '#gz:ec2-start',
    '2',
    '#gz:ec2-end',
    '3'
])
def test_exclude_ec2_config_middle_line(mocked_read_config_file):
    new_lines = ssh.exclude_ec2_config()
    assert len(new_lines) == 2
    assert new_lines[0] == '1'
    assert new_lines[1] == '3'
