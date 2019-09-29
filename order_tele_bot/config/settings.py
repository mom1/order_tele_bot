# -*- coding: utf-8 -*-
# @Author: maxst
# @Date:   2019-09-26 19:27:23
# @Last Modified by:   maxst
# @Last Modified time: 2019-09-29 14:35:19
from pathlib import Path

TOKEN = 'xxx'  # store in .secret file
NAME_BOT = 'xxx'  # store in .secret file

NAME_DB = 'bot.db'

# Base folder
BASE_DIR = Path(__file__).parent.parent

DATABASE = BASE_DIR.joinpath(f'database/{NAME_DB}')
