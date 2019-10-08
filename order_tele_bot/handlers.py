# -*- coding: utf-8 -*-
# @Author: maxst
# @Date:   2019-09-26 21:23:03
# @Last Modified by:   MaxST
# @Last Modified time: 2019-10-08 10:04:36
import logging
from abc import abstractmethod

from dynaconf import settings
from emoji import emojize as _
from telebot import logger

from db import Category, Ware
from markup import Keyboards
from metaclasses import RegistryHolder
from router import router

logger.setLevel(logging.INFO)
nav_menu = [_('<< НАЗАД'), _(':heavy_check_mark: ЗАКАЗ')]


class Handler:
    def __init__(self, bot):
        self.bot = bot
        self.keybords = Keyboards()
        self._observers = {}
        router.source = self

    def run_handlers(self):
        @self.bot.message_handler(func=lambda message: True)
        def echo_all(message):
            self.notify(message.text, msg=message)

        @self.bot.callback_query_handler(func=lambda call: True)
        def callback_worker(call):
            self.notify('order', msg=call, data=call.data)

        self.update_from_category()

    def send_msg(self, msg, *args, **kwargs):
        self.bot.send_message(msg.chat.id, *args, **kwargs)

    def send_cb(self, call, *args, **kwargs):
        kwargs['show_alert'] = True
        self.bot.answer_callback_query(call.id, *args, **kwargs)

    def update_from_category(self):
        events = []
        cat_cmd = CaregoryCommand()
        for cat in Category.all():
            event = f'{cat}'
            if not self.check_event(event):
                router.reg_command(cat_cmd, event)
            events.append(event)
        events.append(nav_menu)
        return events

    def notify(self, event, *args, **kwargs):
        logger.info(f'Свершилось событие {event}')
        kwargs['event'] = event
        kwargs['hand'] = self
        for observer in (self._observers.get(event, []) or []):
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


class AbsCommand(metaclass=RegistryHolder):
    abstract = True

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
    name = _(':open_file_folder: Выбрать товар')
    menu = 'start'

    def update(self, *args, msg=None, hand=None, **kwargs):
        hand.send_msg(msg, 'Каталог категорий товара', reply_markup=hand.keybords.remove_menu())
        hand.send_msg(msg, 'Сделайте свой выбор', reply_markup=hand.keybords.list_kb_menu(menu_items=hand.update_from_category()))


class InfoBot(AbsCommand):
    name = _(':speech_balloon: имя вашего бота')
    menu = 'start'

    def update(self, *args, msg=None, hand=None, **kwargs):
        hand.send_msg(
            msg,
            f'Меня зовут {settings.NAME_BOT}!\nПриятно познакомится :)\nЧем займемся?',
            reply_markup=hand.keybords.kb_menu(self.menu),
        )


class SettingsBot(AbsCommand):
    name = _(':globe_with_meridians: Настройки')
    menu = 'start'

    def update(self, *args, msg=None, hand=None, **kwargs):
        hand.send_msg(msg, f'На данный момент я не настраиваюсь.', reply_markup=hand.keybords.kb_menu(self.menu))


class CaregoryCommand(AbsCommand):
    name = 'Категория'
    abstract = True

    def update(self, *args, msg=None, hand=None, **kwargs):
        cat = Category.find_by(msg.text)
        if not cat:
            hand.send_msg(msg, f'Категория {msg.text} не найдена')
            return
        hand.send_msg(msg, f'Категория {msg.text}', reply_markup=hand.keybords.in_line_kb_menu(menu_items=cat.wares))
        hand.send_msg(msg, 'Ok', reply_markup=hand.keybords.list_kb_menu(menu_items=hand.update_from_category()))


class OrderCallBack(AbsCommand):
    name = 'order'
    product_order = """
    Выбранный товар:

    {}
    Cтоимость: {:.2f} руб

    добавлен в заказ!!!

    На складе осталось {:.2f} ед.
    """.format

    def update(self, *args, msg=None, hand=None, data=None, **kwargs):
        ware = Ware.get(data)
        if not ware:
            logger.error(f'Товар {data} не найден')
            return
        hand.send_cb(msg, self.product_order(ware.title, ware.price, ware.quantity))


router.reg_command(StartCommand, '<< НАЗАД')
