# -*- coding: utf-8 -*-
# @Author: maxst
# @Date:   2019-09-26 21:23:03
# @Last Modified by:   MaxST
# @Last Modified time: 2019-10-14 01:35:37
import logging
from abc import abstractmethod

from dynaconf import settings
from telebot import logger

from db import Category, Order, OrderItems, StateOrder, Ware
from markup import Keyboards
from metaclasses import RegistryHolder
from router import router

logger.setLevel(logging.INFO)


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
            prefix, splitter, data = call.data.partition(':')
            self.notify(prefix, msg=call, data=data)

        self.update_from_category()
        for item_menu in settings.MAIN_MENU:
            self.keybords.reg('start', item_menu)
        for item_menu in settings.ORDER_MENU:
            self.keybords.reg('order', item_menu)

    def send_msg(self, msg, *args, **kwargs):
        self.bot.send_message(msg.chat.id, *args, **kwargs)

    def send_cb(self, call, *args, **kwargs):
        kwargs.setdefault('show_alert', True)
        self.bot.answer_callback_query(call.id, *args, **kwargs)

    def edit_msg_markup(self, msg, *args, **kwargs):
        self.bot.edit_message_reply_markup(msg.chat.id, *args, message_id=msg.message_id, **kwargs)

    def edit_msg_text(self, msg, text, *args, **kwargs):
        self.bot.edit_message_text(text, msg.chat.id, *args, message_id=msg.message_id, **kwargs)

    def update_from_category(self):
        events = []
        cat_cmd = CaregoryCommand()
        for cat in Category.all():
            event = str(cat)
            events.append(event)
            if not self.check_event(event):
                router.reg_command(cat_cmd, event)
        events.append(settings.NAV_MENU)
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
    name = settings.CHOOSE_WARE_ITEM

    def update(self, *args, msg=None, hand=None, **kwargs):
        hand.send_msg(msg, 'Каталог категорий товара', reply_markup=hand.keybords.remove_menu())
        hand.send_msg(msg, 'Сделайте свой выбор', reply_markup=hand.keybords.list_kb_menu(menu_items=hand.update_from_category()))


class InfoBot(AbsCommand):
    name = settings.NAME_BOT_ITEM

    def update(self, *args, msg=None, hand=None, **kwargs):
        hand.send_msg(
            msg,
            settings.APP_INFO,
            parse_mode='HTML',
            reply_markup=hand.keybords.kb_menu('start'),
        )


class SettingsBot(AbsCommand):
    name = settings.SETTINGS_ITEM

    def update(self, *args, msg=None, hand=None, **kwargs):
        hand.send_msg(msg, settings.APP_SETTINGS, parse_mode='HTML', reply_markup=hand.keybords.kb_menu('start'))


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


class AddWareCallBack(AbsCommand):
    name = Ware.short_prefix

    def update(self, *args, msg=None, hand=None, data=None, **kwargs):
        order = Order.filter_by(user_id=msg.from_user.id, state=StateOrder.not_send).first()
        if not order:
            order = Order.create(user_id=msg.from_user.id, number=str(msg.message.message_id))
        ware = Ware.get(data)
        if not ware:
            logger.error(f'Товар {data} не найден')
            return
        try:
            order_item = order.add_item(ware)
        except Exception as e:
            hand.send_cb(msg, str(e), show_alert=False)
            return
        self.answer(*args, msg=msg, hand=hand, ware=ware, order=order, order_item=order_item, **kwargs)

    def answer(self, msg, hand, ware, order, *args, **kwargs):
        hand.edit_msg_markup(msg.message, reply_markup=hand.keybords.in_line_kb_menu(menu_items=ware.caregory.wares))
        hand.send_cb(msg, f'{order}\n\nТовар {ware.title} добавлен')


class AddOrdeItemsCallBack(AddWareCallBack):
    name = f'{OrderItems.short_prefix}_{Ware.short_prefix}'

    def answer(self, msg, hand, order, *args, order_item=None, **kwargs):
        hand.send_cb(msg, f'Товар {order_item.ware.title} добавлен', show_alert=False)
        hand.edit_msg_text(
            msg.message,
            f'{order_item}\nНа складе: {order_item.ware.quantity}',
            reply_markup=hand.keybords.in_line_kb_menu(menu_items=[[
                order_item.make_inline_add(),
                order_item.make_inline_down_quant(),
                order_item.make_inline_del(),
            ]]),
        )


class EditOrderItemCallBack(AbsCommand):
    name = OrderItems.short_prefix

    def update(self, *args, msg=None, hand=None, data=None, **kwargs):
        try:
            order_item = OrderItems.get(data)
        except Exception:
            return
        hand.send_cb(msg, 'Edit', show_alert=False)
        hand.send_msg(msg.message,
                      f'{order_item}\nНа складе: {order_item.ware.quantity}',
                      reply_markup=hand.keybords.in_line_kb_menu(menu_items=[[
                          order_item.make_inline_add(),
                          order_item.make_inline_down_quant(),
                          order_item.make_inline_del(),
                      ]]))


class DelOrderItemCallBack(AbsCommand):
    name = 'del_' + OrderItems.short_prefix

    def update(self, *args, msg=None, hand=None, data=None, **kwargs):
        try:
            order_item = OrderItems.get(data)
        except Exception:
            return

        order = order_item.order
        order_item.delete()

        hand.send_cb(msg, 'Deleted', show_alert=False)
        hand.send_msg(msg.message, order.for_msg(), parse_mode='HTML', reply_markup=hand.keybords.in_line_kb_menu(menu_items=order.make_inline_menu()))


class DownOrderItemCallBack(AbsCommand):
    name = 'down_' + OrderItems.short_prefix

    def update(self, *args, msg=None, hand=None, data=None, **kwargs):
        try:
            order_item = OrderItems.get(data)
        except Exception:
            return

        new_quant = order_item.quantity - 1
        try:
            assert new_quant >= 0, 'Больше уменьшить нельзя'
            order_item.quantity = new_quant
            order_item.save()
        except Exception as e:
            hand.send_cb(msg, str(e), show_alert=False)
            return

        hand.send_cb(msg, 'Edited', show_alert=False)
        hand.edit_msg_text(
            msg.message,
            f'{order_item}\nНа складе: {order_item.ware.quantity}',
            reply_markup=hand.keybords.in_line_kb_menu(menu_items=[[
                order_item.make_inline_add(),
                order_item.make_inline_down_quant(),
                order_item.make_inline_del(),
            ]]),
        )


class OrderCommand(AbsCommand):
    name = settings.ORDER_ITEM

    def update(self, *args, msg=None, hand=None, **kwargs):
        msg_text = 'Нет открытых заказов'
        order = Order.filter_by(user_id=msg.from_user.id, state=StateOrder.not_send).first()
        if order:
            msg_text = order.for_msg()
            hand.send_msg(msg, 'Ваш заказ', reply_markup=hand.keybords.kb_menu('order'))
            hand.send_msg(msg, msg_text, parse_mode='HTML', reply_markup=hand.keybords.in_line_kb_menu(menu_items=order.make_inline_menu()))
        else:
            hand.send_msg(msg, msg_text)


class OrderApplyCommand(AbsCommand):
    name = settings.ORDER_APPLY_ITEM

    def update(self, *args, msg=None, hand=None, **kwargs):
        msg_text = 'Нет открытых заказов'
        order = Order.filter_by(user_id=msg.from_user.id, state=StateOrder.not_send).first()
        if order:
            msg_text = order.for_msg() + settings.BOTTOM_ORDER_APPLY
            order.state = StateOrder.sended
            order.save()
            hand.send_msg(msg, msg_text, parse_mode='HTML', reply_markup=hand.keybords.kb_menu('order'))
        else:
            hand.send_msg(msg, msg_text)


class OrderDelCommand(AbsCommand):
    name = settings.CROSS_ITEM

    def update(self, *args, msg=None, hand=None, **kwargs):
        msg_text = 'Нет открытых заказов'
        order = Order.filter_by(user_id=msg.from_user.id, state=StateOrder.not_send).first()
        if order:
            order.delete()
            hand.send_msg(msg, 'Заказ удален', reply_markup=hand.keybords.kb_menu('start'))
        else:
            hand.send_msg(msg, msg_text, reply_markup=hand.keybords.kb_menu('start'))


router.reg_command(StartCommand, settings.BACK_ITEM)
router.reg_command(ChooseGoods, settings.BACK_TO_CAT_ITEM)
