# -*- coding: utf-8 -*-
# @Author: maxst
# @Date:   2019-09-28 15:05:43
# @Last Modified by:   MaxST
# @Last Modified time: 2019-10-07 21:25:08
from threading import Lock
from abc import ABCMeta


class Singleton(type):
    _lock = Lock()

    def __init__(cls, name, bases, attrs, **kwargs):
        super().__init__(name, bases, attrs)
        cls._instance = None

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__call__(*args, **kwargs)
            return cls._instance


class RegistryHolder(ABCMeta):
    def __new__(cls, name, bases, attrs):
        from router import router
        new_cls = type.__new__(cls, name, bases, attrs)
        if not attrs.get('abstract', False):
            router.reg_command(new_cls)
        return new_cls
