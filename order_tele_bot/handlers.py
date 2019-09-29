# -*- coding: utf-8 -*-
# @Author: maxst
# @Date:   2019-09-26 21:23:03
# @Last Modified by:   MaxST
# @Last Modified time: 2019-09-29 15:32:08
import logging
from abc import ABC, abstractmethod

from dynaconf import settings
from telebot import logger

from db import Category
from markup import Keyboards
from router import router

logger.setLevel(logging.INFO)


class Handler:
    def __init__(self, bot):
        self.bot = bot
        self.keybords = Keyboards()
        self._observers = {}
        self.router = router.init(self)

    def run_handlers(self):
        @self.bot.message_handler(func=lambda message: True)
        def echo_all(message):
            self.notify(message.text, msg=message)

        @self.bot.callback_query_handler(func=lambda call: True)
        def callback_worker(call):
            self.bot.send_message(call.message.chat.id, call.data)

        self.update_from_category()

    def send_msg(self, msg, *args, **kwargs):
        self.bot.send_message(msg.chat.id, *args, **kwargs)

    def update_from_category(self):
        events = []
        for cat in Category.all():
            event = f'{cat}'
            if not self.check_event(event):
                router.reg_command(Caregory.clone(name=event))
            events.append(event)
        return events

    def notify(self, event, *args, **kwargs):
        logger.info(f'Свершилось событие {event}')
        obs = self._observers.get(event, []) or []
        kwargs['event'] = event
        kwargs['hand'] = self
        for observer in obs:
            observer.update(*args, **kwargs)

    def attach(self, observer, event):
        obs = self._observers.get(event, []) or []
        obs.append(observer)
        self._observers[event] = obs
        logger.info(f'{observer} подписался на событие {event}')

    def detach(self, observer, event):
        obs = self._observers.get(event, []) or []
        obs.remove(observer)
        self._observers[event] = obs
        logger.info(f'{observer} отписался от события {event}')

    def check_event(self, name):
        return name in self._observers


class AbsCommand(ABC):
    @abstractmethod
    def update(self, *args, msg=None, hand=None, **kwargs):
        pass

    @classmethod
    def clone(cls, **kwargs):
        return type(f'{cls.__name__}Copy', (cls, ), kwargs)


class StartCommand(AbsCommand):
    name = '/start'

    def update(self, *args, msg=None, hand=None, **kwargs):
        hand.send_msg(
            msg,
            f'{msg.from_user.first_name}, здравствуйте! Жду дальнейших задач.',
            reply_markup=hand.keybords.kb_menu('start'),
        )


class ChooseGoods(AbsCommand):
    name = '📚 Выбрать товар'
    menu = 'start'

    def update(self, *args, msg=None, hand=None, **kwargs):
        hand.send_msg(msg, 'Каталог категорий товара', reply_markup=hand.keybords.remove_menu())
        hand.send_msg(msg, 'Сделайте свой выбор', reply_markup=hand.keybords.list_kb_menu(menu_items=hand.update_from_category()))


class InfoBot(AbsCommand):
    name = 'ℹ имя вашего бота'
    menu = 'start'

    def update(self, *args, msg=None, hand=None, **kwargs):
        hand.send_msg(
            msg,
            f'Меня зовут {settings.NAME_BOT}!\nПриятно познакомится :)\nЧем займемся?',
            reply_markup=hand.keybords.kb_menu(self.menu),
        )


class SettingsBot(AbsCommand):
    name = '⚙ Настройки'
    menu = 'start'

    def update(self, *args, msg=None, hand=None, **kwargs):
        hand.send_msg(msg, f'На данный момент я не настраиваюсь.', reply_markup=hand.keybords.kb_menu(self.menu))


class Caregory(AbsCommand):
    name = 'Категория'

    def update(self, *args, msg=None, hand=None, **kwargs):
        cat = Category.find_by(msg.text)
        if not cat:
            hand.send_msg(msg, f'Категория {msg.text} не найдена')
            return
        hand.send_msg(msg, f'Категория {msg.text}', reply_markup=hand.keybords.in_line_kb_menu(menu_items=cat.wares))
        hand.send_msg(msg, 'Ok', reply_markup=hand.keybords.list_kb_menu(menu_items=hand.update_from_category()))


for cl in (StartCommand, ChooseGoods, InfoBot, SettingsBot):
    router.reg_command(cl)
