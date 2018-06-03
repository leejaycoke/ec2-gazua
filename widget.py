# -*- coding: utf-8 -*-

import re
from urwid import Text
from urwid import CheckBox
from urwid import Frame
from urwid import Edit
from urwid import AttrMap
from urwid import SimpleFocusListWalker
from urwid import SimpleListWalker

from logger import log


class ClippedText(Text):

    def __init__(self, *args, **kwargs):
        super(ClippedText, self).__init__(*args, wrap='clip', **kwargs)


class SearchEdit(AttrMap):

    def __init__(self):
        edit = Edit('Search: ')
        super(SearchEdit, self).__init__(edit, 'header')


class SelectableText(Text):

    def __init__(self, markup, *args, **kwargs):
        super(SelectableText, self).__init__(markup, wrap='clip')

    def selectable(self):
        return True

    def keypress(self, size, key):
        return key


class SSHCheckBox(CheckBox):

    def __init__(self, name, checkable, enter_callback, *args, **kwargs):
        self.checkable = checkable
        self.enter_callback = enter_callback
        super(SSHCheckBox, self).__init__(name, *args, **kwargs)

    def add_instance(self, **kwargs):
        pass

    def keypress(self, size, key):
        if key == 'enter':
            self.enter_callback()
            return

        return super(SSHCheckBox, self).keypress(size, key)

    def set_state(self, state, do_callback=True):
        if not self.checkable:
            return super(SSHCheckBox, self).set_state(False, False)
        return super(SSHCheckBox, self).set_state(state, do_callback)


class GazuaFrame(Frame):
    column_pos = 0

    def __init__(self, *args, **kwargs):
        self.search_edit = Edit('Search: ')
        self.arrow_callback = kwargs['arrow_callback']
        super(GazuaFrame, self).__init__(*args, header=AttrMap(self.search_edit, 'header'))

    def keypress(self, size, key):
        if len(key) == 1 and key.isalpha:
            if re.compile('^[a-zA-Z0-9]$').match(key):
                self.search_edit.insert_text(key)
        elif key == 'backspace':
            self.search_edit.set_edit_text(
                self.search_edit.get_edit_text()[0:-1])
        elif key == 'left':
            if self.column_pos == 0:
                self.arrow_callback(None)
            elif self.column_pos == 1:
                self.column_pos -= 1
                self.arrow_callback(0)
            else:
                self.column_pos -= 1
                self.arrow_callback(1)
        elif key == 'right':
            if self.column_pos == 0:
                self.column_pos += 1
                self.arrow_callback(1)
            elif self.column_pos == 1:
                self.column_pos += 1
                self.arrow_callback(2)
            else:
                self.arrow_callback(None)

        log.info(">>>>> key: " + key)

        return super(GazuaFrame, self).keypress(size, key)


class ExpadableListWalker(SimpleFocusListWalker):

    def set_focus(self, position):
        super(ExpadableListWalker, self).set_focus(position)
