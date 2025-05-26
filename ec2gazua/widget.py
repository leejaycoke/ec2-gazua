# -*- coding: utf-8 -*-

import re

from urwid import AttrMap
from urwid import CheckBox
from urwid import Edit
from urwid import Frame
from urwid import SimpleFocusListWalker
from urwid import Text


class ClippedText(Text):

    def __init__(self, *args, **kwargs):
        super(ClippedText, self).__init__(*args, wrap='clip', **kwargs)


class SelectableText(Text):

    def __init__(self, markup, *args, **kwargs):
        super(SelectableText, self).__init__(markup, wrap='clip')

    def selectable(self):
        return True

    def keypress(self, size, key):
        return key


class SSHCheckBox(CheckBox):
    not_checkable_callback = None

    def __init__(self, label, checkable, enter_callback,
                 not_checkable_callback, *args, **kwargs):
        self.checkable = checkable
        self.enter_callback = enter_callback
        self.not_checkable_callback = not_checkable_callback
        super(SSHCheckBox, self).__init__(label, *args, **kwargs)

    def keypress(self, size, key):
        if key == 'enter':
            self.enter_callback()
            return
        elif key == ' ':  # spacebar
            if not self.checkable and self.not_checkable_callback:
                self.not_checkable_callback(self.label)

        return super(SSHCheckBox, self).keypress(size, key)

    def set_state(self, state, do_callback=True):
        if not self.checkable:
            return super(SSHCheckBox, self).set_state(False, False)
        return super(SSHCheckBox, self).set_state(state, do_callback)


class GazuaFrame(Frame):
    column_pos = 0

    def __init__(self, *args, **kwargs):
        self.arrow_callback = kwargs['arrow_callback']
        super(GazuaFrame, self).__init__(*args)

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

        return super(GazuaFrame, self).keypress(size, key)


class ExpadableListWalker(SimpleFocusListWalker):

    def set_focus(self, position):
        super(ExpadableListWalker, self).set_focus(position)
