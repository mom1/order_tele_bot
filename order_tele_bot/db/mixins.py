# -*- coding: utf-8 -*-
# @Author: maxst
# @Date:   2019-09-28 17:21:23
# @Last Modified by:   MaxST
# @Last Modified time: 2019-10-07 19:48:36
import re

from emoji import get_emoji_regexp


class FindByField:
    field_by = 'title'

    @classmethod
    def find_by(cls, value):
        """Возвращает объект по его полю."""
        val = re.sub(u'\ufe0f', '', (get_emoji_regexp().sub('', value)))
        return cls.query().filter(getattr(cls, f'{cls.field_by}') == val.strip()).first()
