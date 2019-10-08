# -*- coding: utf-8 -*-
# @Author: maxst
# @Date:   2019-09-26 20:14:23
# @Last Modified by:   MaxST
# @Last Modified time: 2019-10-07 19:33:09
import logging
import threading

import sqlalchemy as sa
from dynaconf import settings
from sqlalchemy.engine import Engine
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.declarative.api import as_declarative
from sqlalchemy.orm import scoped_session, sessionmaker

logger = logging.getLogger('client__db')
db_lock = threading.Lock()


class DBManager(object):
    """Менеджер инициатор БД."""
    def __init__(self, *args, **kwargs):
        """Инициализация.

        Args:
            *args: доп. параметры
            **kwargs: доп. параметры

        """
        super().__init__()
        self._setup(*args, **kwargs)

    @staticmethod
    @sa.event.listens_for(Engine, 'connect')
    def set_sqlite_pragma(dbapi_connection, connection_record=None):
        """Параметры подключения к БД.

        Пока не знаю как от этого отделаться при других бекэндах

        Args:
            dbapi_connection: [description]
            connection_record: [description] (default: {None})

        """
        cursor = dbapi_connection.cursor()
        cursor.execute('PRAGMA synchronous = 0')
        cursor.execute('PRAGMA mmap_size = 268435456')
        cursor.execute('PRAGMA cache_size = 20480')  # 20 mb
        cursor.close()

    def _setup(self, *args, **kwargs):
        """Установка БД.

        Args:
            *args: доп. параметры
            **kwargs: доп. параметры

        """

        db_name = settings.DATABASE
        db_name.parent.mkdir(parents=True, exist_ok=True)
        self.engine = sa.create_engine(
            f'sqlite:///{settings.DATABASE}',
            echo=settings.get('DEBUG_SQL', False),
            connect_args={'check_same_thread': False},
        )
        Base.metadata.create_all(self.engine)

        session_factory = sessionmaker(bind=self.engine)
        session = scoped_session(session_factory)

        Core.set_session(session())
        from .tables import Ware, Category
        if len(Ware.all()) == 0:
            Category.delete_all()
            cats = [Category.create(title=title, emoji=emoji) for title, emoji in (
                ('Полуфабрикаты', ':pizza:'),
                ('Баккалея', ':bread:'),
                ('Мороженное', ':shaved_ice:'),
            )]

            for i, cat in enumerate(cats):
                Ware.create(title=f'Товар1_{i}', quantity=10, price=100, active=True, caregory=cat)
                Ware.create(title=f'Товар2_{i}', quantity=10, price=100, active=True, caregory=cat)
                Ware.create(title=f'Товар3_{i}', quantity=10, price=100, active=True, caregory=cat)


@as_declarative()
class Base(object):
    """Базовый класс для таблиц.

    Attributes:
        id: Общее поле оно же ссылка

    """
    @declared_attr
    def __tablename__(cls):  # noqa
        """Имя таблицы в БД для класса

        Args:
            cls: current class

        Returns:
            имя таблицы это имя класса в ловер-кейсе
            str

        """
        return cls.__name__.lower()

    def __repr__(self):
        """Понятный репр для понимания."""
        return f'<{type(self).__name__}s({", ".join(i.key + "=" + str(getattr(self, i.key)) for i in self.__table__.columns)})>'

    id = sa.Column(sa.Integer, primary_key=True)  # noqa


class Core(Base):
    """Ядро для всех таблиц.

    Содержит общие для всех поля и функционал

    Attributes:
        building_type: Тип записи что бы знать из какой таблицы
        created: Дата время создания записи
        updated: Дата время изменения записи
        active: Признак активной записи
        sort: поле сортировки

    """

    building_type = sa.Column(sa.String(32), nullable=False)
    created = sa.Column(sa.DateTime, default=sa.func.now())
    updated = sa.Column(sa.DateTime, default=sa.func.now(), onupdate=sa.func.now())
    active = sa.Column(sa.Boolean, default=False)
    sort = sa.Column(sa.Integer, default=0)

    @declared_attr
    def __mapper_args__(cls):  # noqa
        """Полиморфный маппер.

        Заполняет building_type именем класса

        Args:
            cls: current class

        Returns:
            dict params mapper

        """
        if cls.__name__ == 'Core':
            return {'polymorphic_on': cls.building_type}
        return {'polymorphic_identity': cls.__name__.lower()}

    def fill(self, **kwargs):
        """Заполнение полей объекта.

        Args:
            **kwargs: дикт где ключи имена, а значения значение полей таблицы

        Returns:
            Возвращает тек. объект
            object

        """
        for name, val in kwargs.items():
            setattr(self, name, val)
        return self

    @classmethod
    def set_session(cls, session):
        """Установка текущей сессии.

        Args:
            session: :class:`.Session`

        """
        cls._session = session

    @classmethod
    def query(cls, *args):
        """Возвращает объект для фильтрации и отборов.

        Args:
            *args: доп. параметры.

        Returns:
            Возвращает объект для отборов
            object

        """
        if not args:
            return cls._session.query(cls)
        return cls._session.query(*args)

    @classmethod  # noqa
    def all(cls):
        """Возвращает все записи объекта/таблицы."""
        return cls.query().all()

    @classmethod
    def first(cls):
        """Возвращает первую запись из отбора."""
        return cls.query().first()

    @classmethod
    def create(cls, **kwargs):
        """Создание новой записи.

        Args:
            **kwargs: дикт где ключи имена, а значения значение полей таблицы

        Returns:
            Возвращает созданный объект
            object

        """
        return cls().fill(**kwargs).save()

    def save(self):
        """Сохранение объекта.

        Сохранение всех изменений

        Returns:
            Возвращает сохраненный объект
            object

        """
        self._session.add(self)
        self._session.commit()
        return self

    @classmethod
    def get(cls, id_):
        """Получить один объект по ид.

        Args:
            id_: идентификатор записи для получения

        Returns:
            Возвращает найденный объект
            object

        """
        return cls.query().get(id_)

    @classmethod  # noqa
    def filter(cls, **kwargs):
        """Фильтрация таблицы.

        Стандартная фильтрация с указание полей и значений

        Args:
            **kwargs: параметры фильтрации

        Returns:
            Возвращает результат фильтрации
            object

        """
        return cls.query().filter(**kwargs)

    @classmethod
    def filter_by(cls, **kwargs):
        """Фильтр с упрощенным синтаксисом."""
        return cls.query().filter_by(**kwargs)

    def delete(self):
        """Удаление текущей записи."""
        self._session.delete(self)
        self._session.commit()

    @classmethod
    def delete_qs(cls, qs):
        """Удаление списка записей.

        По одной что бы удалились связанные записи в родительской таблице

        Args:
            qs: queryset for delete

        """
        for item in qs:
            item.delete()
        cls._session.commit()

    @classmethod
    def delete_all(cls):
        """Удалить все записи из заблицы."""
        cls.delete_qs(cls.all())

    @classmethod
    def save_all(cls, qs):
        """Сохранить все записи из списка.

        Args:
            qs: список объектов бд

        """
        for item in qs:
            cls._session.add(item)
        cls._session.commit()
