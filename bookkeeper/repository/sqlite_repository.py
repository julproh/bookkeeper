"""
Модуль описывает репозиторий, работающий с sqlite
"""

import sqlite3
import os
import logging
from typing import Any, Type
from inspect import get_annotations
from bookkeeper.repository.abstract_repository import AbstractRepository, T

logger = logging.getLogger(__name__)


def gettype(attr: Any) -> str:
    """
    Определить тип аттрибута таблиы
    """
    if isinstance(attr, int) or attr is None:
        return 'INTEGER'
    return 'TEXT'


class SqliteRepository(AbstractRepository[T]):
    """
    Репозиторий, работающий c SQLite БД. Хранит данные в файле bookkeeper.db.
    """

    database: str
    table_name: str
    fields: dict
    cls: Type[T]

    def __init__(self, database: str, cls: Type[T]) -> None:
        self.database = database
        self.table_name = cls.__name__.lower()
        self.fields = get_annotations(cls, eval_str=True)
        self.fields.pop('pk')
        self.cls = cls
        if not os.path.exists(database+'.db'):
            with open(database+'.db', 'w'):
                pass
        with sqlite3.connect(self.database) as con:
            values = [(f'{i}', gettype(getattr(cls, i))) for i in self.fields]
            que = ', '.join([f'{i} {tp}' for i, tp in values])
            cur = con.cursor()
            query = (f"""CREATE TABLE IF NOT EXISTS {self.table_name} 
                         (id INTEGER PRIMARY KEY, {que})""")
            cur.execute(query)
        con.close()

    def add(self, obj: T) -> int:
        if getattr(obj, 'pk', None) != 0:
            raise ValueError(f'trying to add object {obj} with filled `pk` attribute')
        names = ', '.join(self.fields.keys())
        values = [getattr(obj, x) for x in self.fields]
        with sqlite3.connect(self.database) as con:
            cur = con.cursor()
            cur.execute('PRAGMA foreign_keys = ON')
            cur.execute(
                f"""INSERT INTO {self.table_name} ({names}) VALUES ({', '.join('?' * len(self.fields))})""",
                values
            )
            if not cur.lastrowid:
                raise ValueError("No assignable pk")
            obj.pk = int(cur.lastrowid)
        con.close()
        return obj.pk

    def get_obj(self, res: Any) -> T:
        """ Получаем объект из БД """

        obj: T = self.cls
        obj.pk = res[0]
        for x, r in zip(self.fields, res[1:]):
            setattr(obj, x, r)
        return obj

    def get(self, pk: int) -> T | None:
        """ Получить объект по id """

        with sqlite3.connect(self.database) as con:
            query = f"""SELECT * FROM {self.table_name} WHERE id = {pk}"""
            cur = con.cursor()
            result = cur.execute(query).fetchone()
            if result is None:
                return None
            obj = self.get_obj(result)
        con.close()
        return obj

    def get_all(self, where: dict[str, Any] | None = None) -> list[T]:
        """
        Получить все записи по некоторому условию
        where - условие в виде словаря {'название_поля': значение}
        если условие не задано (по умолчанию пусто), вернуть все записи
        """

        conditions = ''
        if where:
            condition = ''
            for key, value in where.items():
                condition += f' {key} = {value} AND'
            conditions += condition.rsplit(' ', 1)[0]
            query = f"""SELECT * FROM {self.table_name} WHERE""" + conditions
            print(query)
        else:
            query = f"""SELECT * FROM {self.table_name}"""
        with sqlite3.connect(self.database) as con:
            cur = con.cursor()
            results = cur.execute(query).fetchall()
            print(results)
            objs = [self.get_obj(result) for result in results]
        con.close()
        return objs

    def check_pk(self, cur: Any, pk: int) -> bool:
        """
        Узнать есть ли в БД запись с данным pk.
        """

        res = cur.execute(f"""SELECT * FROM {self.table_name} WHERE id = {pk}""")
        return res is not None

    def update(self, obj: T) -> None:
        """ Обновить данные об объекте. Объект должен содержать поле pk. """

        values = tuple((getattr(obj, x)) for x in self.fields)
        setter = ', '.join([f'{col} = {val}' for col, val in zip(self.fields, values)])
        with sqlite3.connect(self.database) as con:
            if not self.check_pk(con.cursor(), obj.pk):
                raise ValueError(f"""Обновляемой записи с id={obj.pk} не существует в БД.""")
            query = f"""UPDATE {self.table_name} SET {setter} WHERE id = {obj.pk}"""
            con.cursor().execute(query)
        con.close()

    def delete(self, pk: int) -> None:
        """ Удалить запись c заданным pk"""

        with sqlite3.connect(self.database) as con:
            if not self.check_pk(con.cursor(), pk):
                raise KeyError(f"В БД не существует записи с id={pk}.")
            query = f"""DELETE FROM {self.table_name} WHERE id = {pk}"""
            con.cursor().execute(query)
        con.close()
