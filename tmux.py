# -*- coding: utf-8 -*-

import os
import sys

from uuid import uuid4

SESSION_PREFIX = "ec2-gz-"


def create_tmux_command(hostnames):
    session = create_session_name()
    commands = [
        "tmux new-session -s %s -d -x 2000 -y 2000" % session,
        "tmux send-keys -t %s 'ssh %s' C-m" % (session, hostnames[0])
    ]

    is_multi_selection = len(hostnames) > 1
    if is_multi_selection:
        for i, hostname in enumerate(hostnames[1:]):
            commands += [
                "tmux split-window -v -t %s" % session,
                "tmux send-keys -t %s:0.%d 'ssh %s' C-m" % (
                    session, i + 1, hostname)
            ]

    commands += [
        "tmux select-layout 'tiled'",
        "tmux set-window-option synchronize-panes on",
        "tmux attach -t %s" % session
    ]

    return commands


def create_session_name():
    return SESSION_PREFIX + str(uuid4().hex)[:5]


def run(hostnames):
    is_tmux_runnable = len(hostnames) > 0
    if is_tmux_runnable:
        commands = create_tmux_command(hostnames)
        os.system("; ".join(commands))
        sys.exit(0)
