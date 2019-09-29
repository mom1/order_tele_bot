# -*- coding: utf-8 -*-
# @Author: maxst
# @Date:   2019-09-26 19:07:15
# @Last Modified by:   maxst
# @Last Modified time: 2019-09-28 21:26:15
import logging

from dynaconf import settings
from telebot import TeleBot, logger

from db import DBManager
from handlers import Handler
from metaclasses import Singleton


class OrderBot(metaclass=Singleton):

    token = settings.TOKEN

    def __init__(self):
        self.bot = TeleBot(self.token)
        logger.setLevel(logging.INFO)  # Outputs debug messages to console.
        self.db = DBManager()
        self.handler = Handler(self.bot)

    def start(self):
        self.handler.run_handlers()

    def run_bot(self):
        self.start()
        self.bot.polling(none_stop=True)


if __name__ == '__main__':
    bot = OrderBot()
    bot.run_bot()
