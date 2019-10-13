# -*- coding: utf-8 -*-
# @Author: maxst
# @Date:   2019-09-26 19:27:23
# @Last Modified by:   MaxST
# @Last Modified time: 2019-10-14 01:35:48
from pathlib import Path

from emoji import emojize as _

TOKEN = 'xxx'  # store in .secret file
NAME_BOT = 'TalkativeTestBot'  # store in .secret file

NAME_DB = 'bot.db'

# Base folder
BASE_DIR = Path(__file__).parent.parent

DATABASE = BASE_DIR.joinpath(f'database/{NAME_DB}')

# Menu items
CHOOSE_WARE_ITEM = _(':open_file_folder: Выбрать товар')
NAME_BOT_ITEM = _(f':speech_balloon: {NAME_BOT}')
SETTINGS_ITEM = _(':gear: Настройки')
ORDER_ITEM = _(':heavy_check_mark: ЗАКАЗ')
ORDER_APPLY_ITEM = _(':heavy_check_mark: Оформить заказ')
CROSS_ITEM = _('❌')  # del order
UP_ITEM = _(':up_arrow:')
DOWN_ITEM = _(':down_arrow:')
BACK_ITEM = _(':left_arrow: НАЗАД')
BACK_TO_CAT_ITEM = _(':left_arrow: К категориям')
LEFT_ITEM = _(':left_arrow:')
RIGHT_ITEM = _(':right_arrow:')

# Collects Menus
MAIN_MENU = [CHOOSE_WARE_ITEM, [NAME_BOT_ITEM, SETTINGS_ITEM]]
NAV_MENU = [BACK_ITEM, ORDER_ITEM]
ORDER_MENU = [
    [BACK_TO_CAT_ITEM, ORDER_ITEM, CROSS_ITEM],
    ORDER_APPLY_ITEM,
    # [LEFT_ITEM, 0, RIGHT_ITEM],
]

# Messages
APP_INFO = f"""
<b>Добро пожаловать в приложение
            {NAME_BOT} !!!</b>

Данное приложение разработано
специально для торговых представителей,
далее <i>(ТП/СВ)</i>,а также для кладовщиков,
коммерческих организаций осуществляющих
оптово-розничную торговлю.

ТП используя приложение {NAME_BOT},
в удобной интуитивной форме смогут без
особого труда принять заказ от клиента.
{NAME_BOT} поможет сформировать заказ
и в удобном виде адресует кладовщику
фирмы для дальнейшего комплектования заказа.

"""

APP_SETTINGS = f"""
<b>Общее руководство приложением:</b>

-<b>{CHOOSE_WARE_ITEM} - </b><i>Кнопка показывает меню выбора товара по категории</i>
-<b>{NAME_BOT_ITEM} - </b><i>Кнопка показывает информацию о боте</i>
-<b>{SETTINGS_ITEM} - </b><i>Кнопка показывает информацию о настройках</i>
-<b>{ORDER_ITEM} - </b><i>Кнопка показывает информацию о заказе</i>
-<b>{ORDER_APPLY_ITEM} - </b><i>Кнопка отправляет заказ</i>
-<b>{CROSS_ITEM} - </b><i>Удаление строки заказа</i>
-<b>{UP_ITEM} - </b><i>Увеличить</i>
-<b>{DOWN_ITEM} - </b><i>Уменьшить</i>
-<b>{LEFT_ITEM} - </b><i>Назад</i>
-<b>{RIGHT_ITEM} - </b><i>Вперед</i>
"""

ORDER_INFO = """
Заказ №{number} от {date}
<pre>
{order_items}
</pre>
Общее Кол-во: {total_quant:.2f}
К оплате: {total_summ:.2f}
""".format

BOTTOM_ORDER_APPLY = '\n\n<b>ЗАКАЗ НАПРАВЛЕН НА СКЛАД, ДЛЯ ЕГО КОМПЛЕКТОВКИ !!!</b>'
