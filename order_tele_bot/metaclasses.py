# -*- coding: utf-8 -*-
# @Author: maxst
# @Date:   2019-09-28 15:05:43
# @Last Modified by:   maxst
# @Last Modified time: 2019-09-28 15:06:23
from threading import Lock


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
