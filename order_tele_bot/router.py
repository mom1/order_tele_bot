# -*- coding: utf-8 -*-
# @Author: maxst
# @Date:   2019-09-28 20:38:13
# @Last Modified by:   maxst
# @Last Modified time: 2019-09-29 13:50:08


class Router:
    def __init__(self):
        self.commands = []
        self.source = None

    def reg_command(self, command, name=None):
        name = getattr(command, 'name', None) if not name else name
        if name and command:
            self.commands.append((name, command))
            if self.source:
                self.init_cmd(command, name)

    def unreg_command(self, command, name=None):
        name = getattr(command, 'name', None) if not name else name
        self.commands = [(n, c) for n, c in self.commands if n != name]
        if self.source:
            self.source.detach(command, name)

    def init(self, source):
        self.source = source
        for name, cmd in self.commands:
            self.init_cmd(cmd, name)

    def init_cmd(self, cmd, name):
        if hasattr(cmd, '__name__'):
            cmd = cmd()
        self.source.attach(cmd, name)
        menu = getattr(cmd, 'menu', None)
        if menu and hasattr(self.source, 'keybords'):
            self.source.keybords.reg(menu, name)


router = Router()
