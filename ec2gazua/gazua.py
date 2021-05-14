# -*- coding: utf-8 -*-

import urwid

from urwid import Frame

from urwid import Text
from urwid import Columns
from urwid import MainLoop
from urwid import AttrMap
from urwid import LineBox
from urwid import ListBox

from .widget import SelectableText
from .widget import SSHCheckBox
from .widget import GazuaFrame
from .widget import ExpadableListWalker
from .widget import ClippedText

from . import ec2
from . import tmux

from .logger import console


class Footer(object):

    def __init__(self, markup):
        self.widget = Text(markup)

    def set_text(self, markup):
        self.widget.set_text(markup)

    def get_widget(self):
        return AttrMap(self.widget, 'footer')


footer = Footer('EC2 Gazua~!!')


class AWSView(object):
    names = []
    widgets = []
    walker = None
    listbox = None
    view = None

    def __init__(self, names):
        self._init_widgets(names)
        self.update_widgets(names)
        self.update_focus()

    def _init_widgets(self, names):
        self.names = names
        self.widgets = self._create_widgets()
        self.walker = ExpadableListWalker(self.widgets)
        self.listbox = ListBox(self.walker)
        self.view = LineBox(self.listbox, tlcorner='', tline='', lline='',
                            trcorner='', blcorner='', rline='│', bline='',
                            brcorner='')

    def update_widgets(self, names):
        self.names = names
        self.widgets = self._create_widgets()
        self.walker = ExpadableListWalker(self.widgets)
        self.listbox.body = self.walker

    def _create_widgets(self):
        return [self._create_widget(n) for n in self.names]

    def _create_widget(self, name):
        return AttrMap(SelectableText(name), None, {None: 'aws_focus'})

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
        return self.view


class GroupView(object):
    names = []
    widgets = []
    walker = None
    listbox = None
    view = None

    def __init__(self, names):
        self._init_widgets(names)

    def _init_widgets(self, names):
        self.names = names
        self.widgets = self._create_widgets()
        self.walker = ExpadableListWalker(self.widgets)
        self.listbox = ListBox(self.walker)
        self.view = LineBox(self.listbox, tlcorner='', tline='', lline='',
                            trcorner='', blcorner='', rline='│', bline='',
                            brcorner='')

    def update_widgets(self, names):
        self.names = names
        self.widgets = self._create_widgets()
        self.walker = ExpadableListWalker(self.widgets)
        self.listbox.body = self.walker

    def _create_widgets(self):
        return [self._create_widget(n) for n in self.names]

    def _create_widget(self, name):
        return AttrMap(SelectableText(name), None, {None: 'aws_focus'})

    def update_focus(self):
        widget, pos = self.walker.get_focus()
        widget.set_attr_map({None: 'group_focus'})

        prev_widget, _ = self.walker.get_prev(pos)
        if prev_widget:
            prev_widget.set_attr_map({None: None})

        next_widget, _ = self.walker.get_next(pos)
        if next_widget:
            next_widget.set_attr_map({None: None})

    def clear_focus(self):
        widget, _ = self.walker.get_focus()
        widget.set_attr_map({None: None})

    def get_selected_name(self):
        _, pos = self.walker.get_focus()
        return self.names[pos]

    def get_walker(self):
        return self.walker

    def get_widget(self):
        return self.view


class InstanceView(object):
    instances = []
    widgets = []
    walker = None
    listbox = None

    selected_instances = []

    def __init__(self, instances):
        self._init_widgets(instances)

    def _init_widgets(self, instances):
        self.instances = instances
        self.widgets = self._create_widgets()
        self.walker = ExpadableListWalker(self.widgets)
        self.listbox = ListBox(self.walker)

    def update_widgets(self, instances):
        self.instances = instances
        self.widgets = self._create_widgets()
        self.walker = ExpadableListWalker(self.widgets)
        self.listbox.body = self.walker
        self.selected_instances = []

    def _create_widgets(self):
        return [self._create_widget(i) for i in self.instances]

    def _create_widget(self, instance):
        widgets = [
            (25, SSHCheckBox(
                instance.name[:21],
                instance.is_connectable,
                self._run_tmux,
                self.not_checkable_callback,
                on_state_change=self.instance_check_changed,
                user_data=instance)),
            (15, ClippedText(instance.private_ip or '-')),
            (15, ClippedText(instance.public_ip or '-')),
            (15, ClippedText(instance.type[:15])),
            (3, ClippedText('O' if instance.is_running else 'X')),
            ClippedText(instance.key_name or '-'),
        ]

        columns_widget = Columns(widgets, dividechars=1)
        return AttrMap(columns_widget, None, 'instance_focus')

    def not_checkable_callback(self, instance_name):
        footer.set_text("Instance '%s' is not connectable" % instance_name)

    def instance_check_changed(self, widget, state, instance):
        if state:
            self.selected_instances.append(instance)
        else:
            self.selected_instances.remove(instance)

    def get_walker(self):
        return self.walker

    def get_widget(self):
        return self.listbox

    def _run_tmux(self):
        tmux_params = [self._create_tmux_param(i) for i in
                       self.selected_instances]
        tmux.run(tmux_params)

    def _create_tmux_param(self, instance):
        return {
            'ip_address': instance.connect_ip,
            'key_file': instance.key_file,
            'user': instance.user,
        }


class Gazua(object):

    def __init__(self):
        loader = ec2.EC2InstanceLoader()
        self.manager = loader.load_all()
        if len(self.manager.instances) == 0:
            console('There is no instances')
            exit(1)

        self._init_views()

    def _init_views(self):
        aws_names = list(self.manager.aws_names)
        self.aws_view = AWSView(aws_names)

        aws_name = self.aws_view.get_selected_name()
        group_names = list(self.manager.instances[aws_name].keys())
        self.group_view = GroupView(group_names)

        group_name = self.group_view.get_selected_name()
        init_instances = self.manager.instances[aws_name][group_name]
        self.instance_view = InstanceView(init_instances)

        urwid.connect_signal(self.aws_view.get_walker(), "modified",
                             self.on_aws_changed)
        urwid.connect_signal(self.group_view.get_walker(), "modified",
                             self.on_group_changed)

        self.view = Columns([
            (15, self.aws_view.get_widget()),
            (25, self.group_view.get_widget()),
            self.instance_view.get_widget()
        ])

    def on_aws_changed(self):
        # aws
        self.aws_view.update_focus()

        # group
        urwid.disconnect_signal(self.group_view.get_walker(), "modified",
                                self.on_group_changed)
        aws_name = self.aws_view.get_selected_name()
        self.group_view.update_widgets(
            list(self.manager.instances[aws_name].keys()))
        urwid.connect_signal(self.group_view.get_walker(), "modified",
                             self.on_group_changed)

        # instance
        group_name = self.group_view.get_selected_name()
        self.instance_view.update_widgets(
            self.manager.instances[aws_name][group_name])

    def on_group_changed(self):
        aws_name = self.aws_view.get_selected_name()
        group_name = self.group_view.get_selected_name()
        self.instance_view.update_widgets(
            self.manager.instances[aws_name][group_name])
        self.group_view.update_focus()

    def update_group_focus(self):
        self.group_view.update_focus()

    def clear_group_focus(self):
        self.group_view.clear_focus()

    def get_view(self):
        return self.view


gazua = Gazua()


def on_arrow_pressed(column_pos):
    if column_pos == 0:
        gazua.clear_group_focus()
    elif column_pos == 1:
        gazua.update_group_focus()


body = LineBox(gazua.get_view(), tlcorner='═', tline='═', lline='',
               trcorner='═', blcorner='═', rline='', bline='═', brcorner='═')
title_header = AttrMap(Columns([
    (15, Text('aws name      │', wrap='clip')),
    (25, Text('group                   │', wrap='clip')),
    (26, Text('instance name            │', wrap='clip')),
    (16, Text('private ip     │', wrap='clip')),
    (16, Text('public ip      │', wrap='clip')),
    (16, Text('type           │', wrap='clip')),
    (4, Text('run│', wrap='clip')),
    (Text('key', wrap='clip')),
]), 'title_header')

body_frame = Frame(body, header=title_header, footer=footer.get_widget())
wrapper = GazuaFrame(body_frame, arrow_callback=on_arrow_pressed)

palette = [
    ('header', 'white', 'dark red', 'bold'),
    ('footer', 'white', 'light gray', 'bold'),
    ('title_header', 'black', 'dark cyan', 'bold'),
    ('footer', 'black', 'light gray'),
    ('group', 'black', 'yellow', 'bold'),
    ('host', 'black', 'dark green'),
    ('aws_focus', 'black', 'dark green'),
    ('group_focus', 'black', 'dark green'),
    ('instance_focus', 'black', 'yellow'),
]


def key_pressed(key):
    if key == 'esc':
        raise urwid.ExitMainLoop()


def run():
    loop = MainLoop(wrapper, palette, handle_mouse=False,
                    unhandled_input=key_pressed)
    loop.run()
