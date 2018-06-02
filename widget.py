# -*- coding: utf-8 -*-

import re
from urwid import Text
from urwid import CheckBox
from urwid import Frame
from urwid import Edit
from urwid import AttrMap

from logger import log


class SearchEdit(AttrMap):

    def __init__(self):
        edit = Edit('search: ')
        super(SearchEdit, self).__init__(edit, 'header')


class SelectableText(Text):

    def selectable(self):
        return True

    def keypress(self, size, key):
        return key


class SSHCheckBox(CheckBox):

    def __init__(self, enter_callback, *args, **kwargs):
        self.enter_callback = enter_callback
        super(SSHCheckBox, self).__init__(*args, **kwargs)

    def add_instance(self, **kwargs):
        pass

    def keypress(self, size, key):
        if key == 'enter':
            self.enter_callback()
            return

        return super(SSHCheckBox, self).keypress(size, key)


class GazuaFrame(Frame):

    def __init__(self, *args):
        self.search_edit = SearchEdit()
        super(GazuaFrame, self).__init__(*args, header=self.search_edit)

    def keypress(self, size, key):
        if len(key) == 1 and key.isalpha:
            if re.compile('^[a-zA-Z0-9]$').match(key):
                self.search_edit.insert_text(key)
        elif key == 'backspace':
            self.search_edit.set_edit_text(
                self.search_edit.get_edit_text()[0:-1])

        return super(GazuaFrame, self).keypress(size, key)
