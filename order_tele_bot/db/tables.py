# -*- coding: utf-8 -*-
# @Author: maxst
# @Date:   2019-09-28 16:54:27
# @Last Modified by:   MaxST
# @Last Modified time: 2019-10-14 01:35:40
import enum

import sqlalchemy as sa
from dynaconf import settings
from emoji import emojize as _
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import backref, relationship
from sqlalchemy.orm.attributes import get_history
from tabulate import tabulate

from .core import Core, db_lock
from .mixins import FindByField


class Ware(FindByField, Core):
    """Таблица
    """
    short_prefix = 'ware'

    id = sa.Column(sa.Integer, sa.ForeignKey(Core.id, ondelete='CASCADE'), primary_key=True)  # noqa
    title = sa.Column(sa.String(30), unique=True, nullable=False)
    quantity = sa.Column(sa.Integer())
    price = sa.Column(sa.Float(asdecimal=True))
    caregory_id = sa.Column(sa.ForeignKey('category.id', ondelete='CASCADE'))
    caregory = relationship('Category', backref=backref('wares'), foreign_keys=[caregory_id])

    def __str__(self):
        return f'{self.title} Кол-во: {self.quantity:.2f} Цена: {self.price:.2f}'

    def callback_data(self):
        return f'{self.short_prefix}:{self.id}'


class Category(FindByField, Core):
    id = sa.Column(sa.Integer, sa.ForeignKey(Core.id, ondelete='CASCADE'), primary_key=True)  # noqa
    title = sa.Column(sa.String(30), unique=True, nullable=False)
    emoji = sa.Column(sa.String(255))

    def __str__(self):
        return f'{_(self.emoji)} {self.title}'


class StateOrder(enum.Enum):
    """Перечислитель состояний заказов

    Attributes:
        not_send: Не отправлен
        sended: Отправлен

    """

    not_send = 0
    sended = 1


class Order(Core):
    id = sa.Column(sa.Integer, sa.ForeignKey(Core.id, ondelete='CASCADE'), primary_key=True)  # noqa
    number = sa.Column(sa.String(255))
    date = sa.Column(sa.DateTime, default=sa.func.now())
    user_id = sa.Column(sa.Integer())
    state = sa.Column(sa.Enum(StateOrder), default=StateOrder.not_send)

    def __str__(self):
        return f'Заказ №{self.number} от {self.date} Общее Кол-во: {self.total_quant:.2f} К оплате: {self.total_summ:.2f}'

    def for_msg(self):
        order_items = tabulate(
            [i.as_dict() for i in self.order_items],
            headers='keys',
            tablefmt='rst',
        )
        return settings.ORDER_INFO(
            number=self.number,
            date=self.date,
            total_quant=self.total_quant,
            total_summ=self.total_summ,
            order_items=order_items,
        )

    @hybrid_property
    def total_summ(self):
        return sum((i.cost for i in self.order_items))

    @hybrid_property
    def total_quant(self):
        return sum((i.quantity for i in self.order_items))

    def add_item(self, ware):
        dest_item = OrderItems.filter_by(order=self, ware=ware).first()
        if not dest_item:
            dest_item = OrderItems.create(price=ware.price, ware=ware)
            dest_item.sort = len(self.order_items)
        dest_item.quantity += 1
        dest_item.save()
        self.order_items.append(dest_item)
        self.save()
        return dest_item

    def del_item(self, ware):
        dest_item = OrderItems.filter_by(order=self, ware=ware).first()
        if dest_item:
            dest_item.delete()

    def make_inline_menu(self):
        return [i.make_inline_edit() for i in self.order_items]

    def delete(self):
        self.delete_qs(self.order_items)
        return super().delete()


class OrderItems(Core):
    short_prefix = 'order_items'

    id = sa.Column(sa.Integer, sa.ForeignKey(Core.id, ondelete='CASCADE'), primary_key=True)  # noqa
    price = sa.Column(sa.Float(asdecimal=True), default=0)
    quantity = sa.Column(sa.Integer, default=0)

    order_id = sa.Column(sa.ForeignKey('order.id', ondelete='CASCADE'))
    order = relationship('Order', backref=backref('order_items'), foreign_keys=[order_id])
    ware_id = sa.Column(sa.ForeignKey('ware.id', ondelete='CASCADE'))
    ware = relationship('Ware', backref=backref('order_items'), foreign_keys=[ware_id])

    def __str__(self):
        return f'{self.sort}. {self.ware.title} Кол-во:{self.quantity:.2f} Цена: {self.price:.2f} Стоимость: {self.cost:.2f}'

    @hybrid_property
    def cost(self):
        return self.quantity * self.price

    def as_dict(self):
        return {
            '№': self.sort,
            'Товар': self.ware.title,
            'Кол-во': f'{self.quantity:.2f}',
            'Цена': f'{self.price:.2f}',
            'Стоимость': f'{self.cost:.2f}',
        }

    def callback_data(self):
        return f'{self.short_prefix}:{self.id}'

    def make_inline_edit(self):
        return {'text': str(self), 'callback_data': self.callback_data()}

    def make_inline_del(self):
        return {'text': settings.CROSS_ITEM, 'callback_data': 'del_' + self.callback_data()}

    def make_inline_add(self):
        return {
            'text': settings.UP_ITEM,
            'callback_data': f'{self.short_prefix}_{self.ware.short_prefix}:{self.ware.id}',
        }

    def make_inline_down_quant(self):
        return {
            'text': settings.DOWN_ITEM,
            'callback_data': 'down_' + self.callback_data(),
        }

    def save(self):
        with db_lock:
            if self.id and self.has_changes_attr('quantity'):
                old_quan = self.get_old_value('quantity') or 0
                new_quant = self.quantity or 0
                ware_quant = self.ware.quantity
                ware_quant = ware_quant - (new_quant - old_quan)
                self.quantity = old_quan
                assert ware_quant >= 0, 'Не достаточно остатков'
                self.quantity = new_quant
                self.ware.quantity = ware_quant
            return super().save()

    def delete(self):
        with db_lock:
            self.ware.quantity += self.quantity
            return super().delete()

    def get_old_value(self, attr):
        return get_history(self, attr)[2][0]

    def has_changes_attr(self, attr):
        return get_history(self, attr).has_changes()
