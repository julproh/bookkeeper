"""
Модуль описывает репозиторий, работающий c базой данных sqlite
"""

from itertools import count
from inspect import get_annotations
from typing import Any
import sqlite3
import os

from bookkeeper.repository.abstract_repository import AbstractRepository, T


class SqliteRepository(AbstractRepository[T]):
    """
    Репозиторий, работающий с SQLite БД. Хранит данные в файле.
    database - название файла БД
    cls - тип данных
    table_name - название таблицы
    fields -  поля таблицы
    """

    database: str
    cls: type
    table_name: str
    fields: dict

    def __init__(self, database: str, cls: type) -> None:
        """
        Инициализация БД для хранения информации о денежных операциях
        """
        self.database = database
        self.cls = cls
        self.table_name = cls.__name__
        self.fields = get_annotations(cls, eval_str =True)


    def add(self, obj: T) -> int:
        """
        Добавляет объект в репозиторий, возвращает id объекта,
        также записывает id в атрибут pk.
        """
        if getattr(obj, 'pk', None) != 0:
            raise ValueError(f'trying to add object {obj} with filled `pk` attribute')
        fields = ', '.join(self.fields.keys())
        placeholders = ', '.join('?' * len(self.fields))
        values = tuple(getattr(obj, x) for x in self.fields.keys())
        with sqlite3.connect(self.database) as conn:
            cur = conn.cursor()
            cur.execute(
                f"INSERT INTO {self.table_name} ({fields}) VALUES ({placeholders})", values
            )
            obj.pk = int(cur.lastrowid)
            cur.execute(
                f'UPDATE {self.table_name} SET pk = {obj.pk} '
                f'WHERE ROWID = {obj.pk}'
            )
        conn.close()
        return obj.pk

    def get(self, pk: int) -> T | None:
        """
        Получаем объект по id.
        """
        with sqlite3.connect(self.database) as conn:
            cur = conn.cursor()
            cur.execute(
                f'SELECT * FROM {self.table_name} WHERE pk = {pk}'
            )
            tuple_obj = cur.fetchone()
        conn.close()
        obj = self.cls(tuple_obj)
        return obj

    def get_all(self, where: dict[str, Any] | None = None) -> list[T]:
        """
        Получить все записи таблицы по некоторому условию.
        """
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            cur.execute(f"SELECT * FROM {self.table_name}")
            tuple_objs = cur.fetchall()
        con.close()
        objs = []
        fields = (*[str(k) for k in self.fields.keys()], 'pk')
        for tuple_obj in tuple_objs:
            obj = self.cls()
            for i in range(len(fields)):
                setattr(obj, fields[i], tuple_obj[i])
            objs.append(obj)
        if where is None:
            return objs
        objs = [
            obj for obj in objs if all(
                getattr(obj, attr) == where[attr] for attr in where.keys()
            )
        ]
        return objs

    def update(self, obj: T) -> None:
        """
        Изменение объекта, уже записанного в репозиторий.
        """
        if obj.pk == 0:
            raise ValueError('Attempt to update object with unknown primary key. Please, correct the object.')
        fields = list(self.fields.keys())
        values = ', '.join(f"{field} = \'{getattr(obj, field)}\'" for field in fields)
        with sqlite3.connect(self.database) as conn:
            cur = conn.cursor()
            cur.execute(f"UPDATE {self.table_name} SET {values} WHERE pk = {obj.pk}")
        conn.close()

    def delete(self, pk: int) -> None:
        """Удаление объекта из репозитория по его id"""
        if self.get(pk) is None:
            raise KeyError
        with sqlite3.connect(self.database) as conn:
            cur = conn.cursor()
            cur.execute(f"DELETE FROM {self.table_name} WHERE pk = {pk}")
            conn.close()
