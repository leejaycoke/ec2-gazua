# -*- coding: utf-8 -*-

import boto3

from collections import OrderedDict

from os.path import expanduser
from os.path import isfile

from ec2gazua.config import Config
from ec2gazua.logger import console
from ec2gazua.logger import log


class EC2InstanceManager(object):
    instances = {}

    def add_instance(self, aws_name, group, instance):
        if aws_name not in self.instances:
            self.instances[aws_name] = {}

        if group not in self.instances[aws_name]:
            self.instances[aws_name][group] = []

        self.instances[aws_name][group].append(instance)

    @property
    def aws_names(self):
        return self.instances.keys()

    def sort(self):
        sorted_instances = OrderedDict()

        for aws_name, groups in OrderedDict(
                sorted(self.instances.items(),
                       key=lambda x: x[0])).items():

            sorted_instances[aws_name] = {}

            for group, instances in OrderedDict(
                    sorted(groups.items(), key=lambda x: x[0])).items():
                instances.sort(key=lambda x: x.name)
                sorted_instances[aws_name][group] = instances

        self.instances = sorted_instances


class EC2InstanceLoader(object):
    config = Config()

    def _request_instances(self, aws_name):
        credential = self.config[aws_name]['credential']
        session = boto3.Session(
            aws_access_key_id=credential['aws_access_key_id'],
            aws_secret_access_key=credential['aws_secret_access_key'],
            region_name=credential['region'])

        client = session.client('ec2')

        instances = []
        for revs in client.describe_instances()['Reservations']:
            instances += revs['Instances']
        return instances

    def load_all(self):
        manager = EC2InstanceManager()

        for aws_name, item in self.config.items():
            console('Instance loading [%s]' % aws_name)
            aws_instances = self._request_instances(aws_name)

            for aws_instance in aws_instances:
                ec2_instance = EC2Instance(self.config[aws_name], aws_instance)

                if self.config[aws_name]['filter'][
                    'connectable'] and not ec2_instance.is_connectable:
                    continue

                manager.add_instance(aws_name, ec2_instance.group,
                                     ec2_instance)

        manager.sort()

        return manager


class EC2Instance(object):
    DEFAULT_NAME = "UNKNOWN-NAME"
    DEFAULT_GROUP = "UNKNOWN-GROUP"

    def __init__(self, config, instance):
        self.config = config
        self.instance = instance

    @property
    def tags(self):
        return {t['Key']: t['Value'] for t in self.instance.get('Tags', {}) if
                t['Value'] != ''}

    @property
    def id(self):
        return self.instance['InstanceId']

    @property
    def name(self):
        if self.config['name-tag'] in self.tags:
            return self.tags[self.config['name-tag']]
        return self.id

    @property
    def group(self):
        if self.config['group-tag'] in self.tags:
            return self.tags[self.config['group-tag']]
        return self.DEFAULT_GROUP

    @property
    def type(self):
        return self.instance['InstanceType']

    @property
    def key_name(self):
        option = self.config['key-file']['default']
        key_name = self.instance.get('KeyName') if option == 'auto' else option
        override = self.config['key-file']
        for group, value in override.get('group', {}).items():
            if group in self.group:
                key_name = value
        for name, value in override.get('name', {}).items():
            if name in self.name:
                key_name = value
        return key_name

    @property
    def key_file(self):
        if self.key_name is None:
            return None

        key_file = self.config['ssh-path'] + '/' + self.key_name
        key_path = expanduser(key_file)

        if isfile(key_path):
            return key_path

        if key_path.endswith('.pem'):
            return key_path if isfile(key_path) else None

        pem_path = key_path + '.pem'
        return pem_path if isfile(pem_path) else None

    @property
    def private_ip(self):
        return self.instance.get('PrivateIpAddress')

    @property
    def public_ip(self):
        return self.instance.get('PublicIpAddress')

    @property
    def connect_ip(self):
        ip_type = self.config['connect-ip']['default']
        override = self.config['connect-ip']
        for group, value in override.get('group', {}).items():
            if group in self.group:
                ip_type = value
        for name, value in override.get('name', {}).items():
            if name in self.name:
                ip_type = value
        return self.public_ip if ip_type == 'public' else self.private_ip

    @property
    def user(self):
        user = self.config['user']['default']
        override = self.config['user']
        for group, value in override.get('group', {}).items():
            if group in self.group:
                user = value
        for name, value in override.get('name', {}).items():
            if name in self.name:
                user = value
        return user

    @property
    def has_key_file(self):
        return self.key_file is not None

    @property
    def is_running(self):
        log.info(self.instance['State'])
        return self.instance['State']['Name'] == 'running'

    @property
    def is_connectable(self):
        return self.is_running and self.has_key_file and \
               self.connect_ip is not None
