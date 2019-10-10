# -*- coding: utf-8 -*-
# @Author: maxst
# @Date:   2019-09-28 16:54:27
# @Last Modified by:   MaxST
# @Last Modified time: 2019-10-10 21:53:37
import sqlalchemy as sa
from emoji import emojize as _
from sqlalchemy.orm import backref, relationship

from .core import Core
from .mixins import FindByField


class Ware(FindByField, Core):
    """Таблица
    """

    id = sa.Column(sa.Integer, sa.ForeignKey(Core.id, ondelete='CASCADE'), primary_key=True)  # noqa
    title = sa.Column(sa.String(30), unique=True, nullable=False)
    quantity = sa.Column(sa.Integer())
    price = sa.Column(sa.Float(asdecimal=True))
    caregory_id = sa.Column(sa.ForeignKey('category.id', ondelete='CASCADE'))
    caregory = relationship('Category', backref=backref('wares'), foreign_keys=[caregory_id])

    def __str__(self):
        return f'{self.title} Кол-во: {self.price:.2f} Цена: {self.quantity}'


class Category(FindByField, Core):
    id = sa.Column(sa.Integer, sa.ForeignKey(Core.id, ondelete='CASCADE'), primary_key=True)  # noqa
    title = sa.Column(sa.String(30), unique=True, nullable=False)
    emoji = sa.Column(sa.String(255))

    def __str__(self):
        return f'{_(self.emoji)} {self.title}'


class Order(Core):
    id = sa.Column(sa.Integer, sa.ForeignKey(Core.id, ondelete='CASCADE'), primary_key=True)  # noqa
    number = sa.Column(sa.String(255))
    data = sa.Column(sa.DateTime, default=sa.func.now())
    # user_id = sa.Column(sa.ForeignKey('user.id', ondelete='CASCADE'))
    # total_quant = sa.Column(sa.Integer())
    # total_summ = sa.Column(sa.Integer())

    # def __str__(self):
    #     return f'{self.number} от {self.data} Кол-во: {self.total_quant:.2f} Стоимость: {self.total_summ:.2f}'
