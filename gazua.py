# -*- coding: utf-8 -*-

import threading

import os
import sys
import collections
import time

import urwid
import ssh
import ec2

from uuid import uuid4

from logger import log

from widget import SelectableText
from widget import SSHCheckBox
from widget import GazuaFrame

from urwid import Edit
from urwid import Text
from urwid import Columns
from urwid import MainLoop
from urwid import AttrMap
from urwid import LineBox
from urwid import ListBox
from widget import ExpadableListWalker

LOAD_EC2 = Text('[F2]Load EC2')
DELETE_EC2 = Text('[F3]Delete EC2')
FOOTER = AttrMap(Columns([(15, LOAD_EC2), DELETE_EC2]), 'footer')

SESSION_NAME_PREFIX = "gz-"


# SELECTED_HOSTS = []
# GROUP_WIDGETS = []
# HOST_WIDGETS = collections.OrderedDict()
#
# aws_widgets = []
# group_widgets = []


def create_tmux_command():
    session = create_session_name()
    commands = [
        "tmux new-session -s %s -d -x 2000 -y 2000" % session,
        "tmux send-keys -t %s 'ssh %s' C-m" % (session, SELECTED_HOSTS[0])
    ]

    is_multi_selection = len(SELECTED_HOSTS) > 1
    if is_multi_selection:
        for i, hostname in enumerate(SELECTED_HOSTS[1:]):
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
    return SESSION_NAME_PREFIX + str(uuid4().hex)


def run_tmux():
    is_tmux_runnable = len(SELECTED_HOSTS) > 0
    if is_tmux_runnable:
        commands = create_tmux_command()
        os.system("; ".join(commands))
        sys.exit(0)


# def on_group_changed():
#     focus_item = group_listbox.get_focus()
#
#     for group_widget in GROUP_WIDGETS:
#         if group_widget == focus_item[0]:
#             group_widget.set_attr_map({None: 'group_focus'})
#         else:
#             group_widget.set_attr_map({None: None})
#
#     group_widget = focus_item[0].original_widget[0].text
#
#     host_listbox.body = ExpadableListWalker(HOST_WIDGETS[group_widget])
#
#     for widget_attrs in HOST_WIDGETS.values():
#         for host_attr in widget_attrs:
#             host_attr.original_widget[0].set_state(False)

class AWSView(object):

    def __init__(self, names):
        self.names = names
        self._init_widgets()

    def _init_widgets(self):
        self.widgets = []

        for name in self.names:
            widget = AttrMap(SelectableText(name), None, {None: 'aws_focus'})
            self.widgets.append(widget)

        self.walker = ExpadableListWalker(self.widgets)
        self.listbox = ListBox(self.walker)

    def on_changed(self):
        log.info('on_aws_changed')
        self.update_focus()

    def update_focus(self):
        widget, pos = self.walker.get_focus()
        widget.set_attr_map({None: 'aws_focus'})

        prev_widget, _ = self.walker.get_prev(pos)
        if prev_widget:
            prev_widget.set_attr_map({None: None})

        next_widget, _ = self.walker.get_next(pos)
        if next_widget:
            next_widget.set_attr_map({None: None})

    def get_selected_name(self):
        _, pos = self.walker.get_focus()
        return self.names[pos]

    def get_walker(self):
        return self.walker

    def get_widget(self):
        return self.listbox


class GroupView(object):
    names = []
    widgets = []
    walker = None

    def __init__(self):
        self._init_widgets()

    def _init_widgets(self):
        self.widgets = []
        self.walker = ExpadableListWalker(self.widgets)
        self.listbox = ListBox(self.walker)

    def on_changed(self):
        log.info('on_group_changed')
        self.update_focus()

    def update_focus(self):
        widget, pos = self.walker.get_focus()
        widget.set_attr_map({None: 'group_focus'})

        prev_widget, _ = self.walker.get_prev(pos)
        if prev_widget:
            prev_widget.set_attr_map({None: None})

        next_widget, _ = self.walker.get_next(pos)
        if next_widget:
            next_widget.set_attr_map({None: None})

    def get_selected_name(self):
        _, pos = self.walker.get_focus()
        return self.names[pos]

    def get_walker(self):
        return self.walker

    def get_widget(self):
        return self.listbox


class InstanceView(object):

    def __init__(self, instances):
        self.instances = instances
        self._init_widgets()

    def _init_widgets(self):
        self.widgets = []

        for i in self.instances:
            widget = AttrMap(SelectableText(i['name']), None, 'instance_focus')
            self.widgets.append(widget)

        self.walker = ExpadableListWalker(self.widgets)
        self.listbox = ListBox(self.walker)

    def on_changed(self):
        log.info('on_i_changed')

    def get_walker(self):
        return self.walker

    def get_widget(self):
        return self.listbox


class Gazua(object):

    def __init__(self):
        i = ec2.get_instances()
        i['minor'] = i['major']
        self.instances = i
        self._init_views()

    def _init_views(self):
        aws_names = self.instances.keys()
        self.aws_view = AWSView(aws_names)

        # aws_name = self.aws_view.get_selected_name()
        # group_names = self.instances[aws_name].keys()
        self.group_view = GroupView()

        # group_name = self.group_view.get_selected_name()
        # init_instances = self.instances[aws_name][group_name]
        self.instance_view = InstanceView([])

        urwid.connect_signal(self.aws_view.get_walker(), "modified", self.on_aws_changed)
        urwid.connect_signal(self.group_view.get_walker(), "modified", self.on_group_changed)

        self.view = Columns([
            (15, self.aws_view.get_widget()),
            (25, self.group_view.get_widget()),
            self.instance_view.get_widget()
        ])

        self.aws_view.walker._modified()

    def on_aws_changed(self):
        pass
        # self.aws_view.on_changed()
        #
        # aws_name = self.aws_view.get_selected_name()
        # self.group_view.update(self.instances[aws_name].keys())
        # self.group_view.on_changed()

    def on_group_changed(self):
        pass
        self.group_view.on_changed()

    def clear_group_focus(self):
        pass
        self.group_view.clear_focus()

    def get_view(self):
        return self.view


# for group, hosts in configs.items():
#
#     if group not in HOST_WIDGETS:
#         HOST_WIDGETS[group] = []
#
#     for host, values in hosts.items():
#         host_widget = SSHCheckBox(run_tmux, host)
#
#         ipaddr = values.get('HostName', 'unknown')
#         ipaddr_widget = Text(ipaddr, align='left')
#
#         column_widget = Columns([host_widget, ipaddr_widget], dividechars=2)
#         urwid.connect_signal(host_widget, 'change', on_host_selected, host)
#
#         host_widget = AttrMap(column_widget, None, 'instance_focus')
#         HOST_WIDGETS[group].append(host_widget)
#
#     group_widget = SelectableText(group, wrap='clip')
#     count_widget = Text(str(len(hosts)), align='right')
#     arrow_widget = Text(">", align='right')
#     column_widget = Columns(
#         [group_widget, count_widget, arrow_widget], dividechars=2)
#     group_widget = AttrMap(column_widget, None)
#     GROUP_WIDGETS.append(group_widget)
#
# group_model = ExpadableListWalker(GROUP_WIDGETS)
# group_listbox = ListBox(group_model)
# group_box = LineBox(group_listbox, tlcorner='', tline='', lline='',
#                     trcorner='', blcorner='', rline='│', bline='', brcorner='')
# urwid.connect_signal(group_model, "modified", on_group_changed)
#
# first_host_widget = HOST_WIDGETS[HOST_WIDGETS.keys()[0]]
# host_model = ExpadableListWalker(first_host_widget)
# host_listbox = ListBox(host_model)
# host_box = LineBox(host_listbox, tlcorner='', tline='', lline='',
#                    trcorner='', blcorner='', rline='', bline='', brcorner='')
#
# GROUP_WIDGETS[0].set_attr_map({None: 'group_focus'})
#
# columns = Columns([(50, group_box), host_box])
gazua = Gazua()
body = LineBox(gazua.get_view())

palette = [
    ('header', 'white', 'dark red', 'bold'),
    ('footer', 'black', 'light gray'),
    ('group', 'black', 'yellow', 'bold'),
    ('host', 'black', 'dark green'),
    ('aws_focus', 'black', 'dark green'),
    ('group_focus', 'black', 'dark green'),
    ('instance_focus', 'black', 'yellow'),
]


def me(column_pos):
    # if column_pos == 0:
        # gazua.clear_group_focus()
    #     gazua.set_aws_focus()
    # if column_pos == 1:
    pass


frame = GazuaFrame(body, arrow_callback=me)


def load_ec2():
    pass


def key_pressed(key):
    if key == 'esc':
        raise urwid.ExitMainLoop()
    elif key == 'f2':
        load_ec2()
    elif key == 'f3':
        pass
        # delete_ec2()


def refreshScreen(mainloop):
    while True:
        mainloop.draw_screen()
        time.sleep(1)


loop = MainLoop(frame, palette, handle_mouse=True,
                unhandled_input=key_pressed)
# refresh = threading.Thread(target=refreshScreen, args=(loop,))
# refresh.start()

loop.run()
