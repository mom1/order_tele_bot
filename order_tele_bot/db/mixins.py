# -*- coding: utf-8 -*-
# @Author: maxst
# @Date:   2019-09-28 17:21:23
# @Last Modified by:   maxst
# @Last Modified time: 2019-09-28 18:17:09


class FindByField:
    field_by = 'title'

    @classmethod
    def find_by(cls, value):
        """Возвращает объект по его полю."""
        return cls.query().filter(getattr(cls, f'{cls.field_by}') == value).first()
