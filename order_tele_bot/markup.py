# -*- coding: utf-8 -*-
# @Author: maxst
# @Date:   2019-09-26 21:27:45
# @Last Modified by:   MaxST
# @Last Modified time: 2019-10-08 09:59:16
from telebot.types import (
    InlineKeyboardButton, InlineKeyboardMarkup,
    KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove,
)


class Keyboards:
    def __init__(self):
        self.all_menu = {}

    def reg(self, menu, name):
        obs = self.all_menu.get(menu, []) or []
        obs.append(name)
        self.all_menu[menu] = obs

    def unreg(self, menu, name):
        obs = self.all_menu.get(menu, []) or []
        obs.remove(name)
        self._observers[menu] = obs

    def set_btn(self, name):
        return KeyboardButton(name)

    def set_inline_btn(self, item):
        kwargs = {}
        if hasattr(item, 'id'):
            kwargs['callback_data'] = str(item.id)
        return InlineKeyboardButton(str(item), **kwargs)

    def remove_menu(self):
        return ReplyKeyboardRemove()

    def kb_menu(self, menu=None, menu_items=None, **kwargs):
        kwargs.setdefault('resize_keyboard', True)
        return self._make_markup(
            ReplyKeyboardMarkup,
            self.all_menu.get(menu, None) or menu_items or [],
            self.set_btn,
            **kwargs,
        )

    def list_kb_menu(self, menu=None, menu_items=None, **kwargs):
        kwargs.setdefault('row_width', 1)
        return self._make_markup(
            ReplyKeyboardMarkup,
            self.all_menu.get(menu, None) or menu_items or [],
            self.set_btn,
            **kwargs,
        )

    def in_line_kb_menu(self, menu=None, menu_items=None, **kwargs):
        kwargs.setdefault('row_width', 1)
        return self._make_markup(
            InlineKeyboardMarkup,
            self.all_menu.get(menu, None) or menu_items or [],
            self.set_inline_btn,
            **kwargs,
        )

    def _make_markup(self, cl, items_menu, wrap_item=None, **kwargs):
        markup = cl(**kwargs)
        for item_menu in items_menu:
            if isinstance(item_menu, (list, tuple)):
                markup.row(*(map(wrap_item, item_menu) if wrap_item else item_menu))
            else:
                markup.add(wrap_item(item_menu) if wrap_item else item_menu)
        return markup
