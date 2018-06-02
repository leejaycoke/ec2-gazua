# -*- coding: utf-8 -*-

import ec2

import mock

import ec2_dummy


mocked_content = """
credential:
    aws_access_key_id: xx1
    aws_secret_access_key: xx2
    region: 'ap-northeast-2'

tag:
    group: Group
    name: Name

identity-file:
    default: ~/.ssh/id_rsa_test
    group:
        billing: ~/.ssh/id_rsa_billing
        purch: ~/.ssh/id_rsa_purch
    name:
        billing_was1: ~/.ssh/id_rsa_billing2
        st-live-db: ~/.ssh/id_rsa_settler2

hostname:
    default: public_ip
    group:
      live-company-group: private_ip
    name:
      private-my-server: public_dns
"""


@mock.patch('ec2.read_config_file', return_value=mocked_content)
def test_config(mocked_read_config_file):
    config = ec2.get_config()
    assert config['credential']['aws_access_key_id'] == 'xx1'
    assert config['credential']['aws_secret_access_key'] == 'xx2'
    assert config['credential']['region'] == 'ap-northeast-2'


def test_ec2_list():
    ec2_list = ec2.get_list()
    print ec2_list
