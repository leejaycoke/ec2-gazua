import urwid

from urwid import Text, Columns, MainLoop, AttrMap, LineBox, ListBox, Pile

from .widget import SelectableText, SSHCheckBox, GazuaFrame, ExpadableListWalker, ClippedText
from . import ec2, tmux
from .logger import console


class AWSView:
    def __init__(self, names):
        self._init_widgets(names)
        self.update_widgets(names)
        self.update_focus()

    def _init_widgets(self, names):
        self.names = names
        self.widgets = self._create_widgets()
        self.walker = ExpadableListWalker(self.widgets)
        self.listbox = ListBox(self.walker)

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
        return self.listbox


class GroupView:
    def __init__(self, names):
        self._init_widgets(names)

    def _init_widgets(self, names):
        self.names = names
        self.widgets = self._create_widgets()
        self.walker = ExpadableListWalker(self.widgets)
        self.listbox = ListBox(self.walker)

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
        return self.listbox


class InstanceView:
    def __init__(self, instances):
        self._init_widgets(instances)

    def _init_widgets(self, instances):
        self.instances = instances
        self.widgets = self._create_widgets()
        self.walker = ExpadableListWalker(self.widgets)
        self.listbox = ListBox(self.walker)
        self.selected_instances = []

    def update_widgets(self, instances):
        self.instances = instances
        self.widgets = self._create_widgets()
        self.walker = ExpadableListWalker(self.widgets)
        self.listbox.body = self.walker
        self.selected_instances = []

    def _create_widgets(self):
        return [self._create_widget(i) for i in self.instances]

    def _create_widget(self, instance):
        items = [
            ('weight', 5, SSHCheckBox(
                instance.name,
                instance.is_connectable,
                self._run_tmux,
                self._noop_callback,
                on_state_change=self.instance_check_changed,
                user_data=instance)),
            ('weight', 1, ClippedText(instance.private_ip or '-')),
            ('weight', 1, ClippedText(instance.public_ip or '-')),
            ('weight', 1, ClippedText(instance.type[:15])),
            ('weight', 1, ClippedText('O' if instance.is_running else 'X', align='center')),
        ]
        columns = Columns(items, dividechars=1)
        return AttrMap(columns, None, {None: 'instance_focus'})

    def _noop_callback(self, *args):
        pass

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
        tmux_params = [self._create_tmux_param(i) for i in self.selected_instances]
        tmux.run(tmux_params)

    def _create_tmux_param(self, instance):
        return {
            'ip_address': instance.connect_ip,
            'key_file': instance.key_file,
            'user': instance.user,
        }


class Gazua:
    def __init__(self):
        loader = ec2.EC2InstanceLoader()
        self.manager = loader.load_all()
        if not self.manager.instances:
            console('There is no instances')
            exit(1)
        self._init_views()

    def _init_views(self):
        aws_names = list(self.manager.aws_names)
        self.aws_view = AWSView(aws_names)

        group_names = list(self.manager.instances[self.aws_view.get_selected_name()].keys())
        self.group_view = GroupView(group_names)

        init_instances = self.manager.instances[
            self.aws_view.get_selected_name()][
            self.group_view.get_selected_name()]
        self.instance_view = InstanceView(init_instances)

        urwid.connect_signal(self.aws_view.get_walker(), 'modified', self.on_aws_changed)
        urwid.connect_signal(self.group_view.get_walker(), 'modified', self.on_group_changed)

        header_cols = Columns([
            ('weight', 5, Text('Instance Name', align='left')),
            ('weight', 1, Text('Private IP',    align='left')),
            ('weight', 1, Text('Public IP',     align='left')),
            ('weight', 1, Text('Type',          align='left')),
            ('weight', 1, Text('Running',           align='center')),
        ], dividechars=1)

        header = AttrMap(header_cols, 'column_header')

        instance_panel = LineBox(
            Pile([
                ('pack', header),
                self.instance_view.get_widget(),
            ]),
            title='Instances'
        )

        self.view = Columns([
            ('weight', 1, LineBox(self.aws_view.get_widget(),   title='AWS')),
            ('weight', 2, LineBox(self.group_view.get_widget(), title='Group')),
            ('weight', 6, instance_panel),
        ], dividechars=1)

    def on_aws_changed(self):
        self.aws_view.update_focus()
        urwid.disconnect_signal(self.group_view.get_walker(), 'modified', self.on_group_changed)
        aws = self.aws_view.get_selected_name()
        self.group_view.update_widgets(list(self.manager.instances[aws].keys()))
        urwid.connect_signal(self.group_view.get_walker(), 'modified', self.on_group_changed)
        self.on_group_changed()

    def on_group_changed(self):
        aws = self.aws_view.get_selected_name()
        group = self.group_view.get_selected_name()
        self.instance_view.update_widgets(self.manager.instances[aws][group])
        self.group_view.update_focus()

    def get_view(self):
        return self.view


def run():
    gazua = Gazua()
    wrapper = GazuaFrame(gazua.get_view(), arrow_callback=lambda x: None)

    palette = [
        ('title_header',   'black',      'dark cyan', 'bold'),
        ('aws_focus',      'black',      'dark green'),
        ('group_focus',    'black',      'dark green'),
        ('instance_focus', 'black',      'yellow'),
    ]

    def key_pressed(key):
        if key == 'esc':
            raise urwid.ExitMainLoop()

    loop = MainLoop(wrapper, palette, handle_mouse=False,
                    unhandled_input=key_pressed)
    loop.run()
