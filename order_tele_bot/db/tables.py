# -*- coding: utf-8 -*-
# @Author: maxst
# @Date:   2019-09-28 16:54:27
# @Last Modified by:   maxst
# @Last Modified time: 2019-09-28 17:27:13
import sqlalchemy as sa
from sqlalchemy import func
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

    def __str__(self):
        return f'{self.title}'
