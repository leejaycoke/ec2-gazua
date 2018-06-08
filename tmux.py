# -*- coding: utf-8 -*-

import os
import sys

from uuid import uuid4

SESSION_PREFIX = "ec2-gz-"


def create_tmux_command(ssh_params):
    session = create_session_name()
    commands = [
        "tmux new-session -s %s -d -x 2000 -y 2000" % session,
        "tmux send-keys -t %s 'ssh %s@%s -i %s -o StrictHostKeyChecking=no' C-m" % (
            session,
            ssh_params[0]['user'],
            ssh_params[0]['ip_address'],
            ssh_params[0]['key_file'] if ssh_params[0]['key_file'] is not None else 'NOT_FOUND_KEY_FILE')
    ]

    if len(ssh_params) > 1:
        for i, ssh_param in enumerate(ssh_params[1:]):
            commands += [
                "tmux split-window -v -t %s" % session,
                "tmux send-keys -t %s:0.%d 'ssh %s@%s -i %s -o StrictHostKeyChecking=no' C-m" % (
                    session,
                    i + 1,
                    ssh_param['user'],
                    ssh_param['ip_address'],
                    ssh_param['key_file'] if ssh_params[0]['key_file'] is not None else 'NOT_FOUND_KEY_FILE'
                )
            ]

    commands += [
        "tmux select-layout 'tiled'",
        "tmux set-window-option synchronize-panes on",
        "tmux attach -t %s" % session
    ]

    return commands


def create_session_name():
    return SESSION_PREFIX + str(uuid4().hex)[:5]


def run(ssh_params):
    if len(ssh_params) > 0:
        commands = create_tmux_command(ssh_params)
        os.system("; ".join(commands))
        sys.exit(0)
