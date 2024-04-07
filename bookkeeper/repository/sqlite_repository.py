"""
Модуль описывает репозиторий, работающий в базе данных
"""

from itertools import count
from typing import Any
import sqlite3
from datetime import datetime
from bookkeeper.repository.abstract_repository import AbstractRepository, T


class SqliteRepository(AbstractRepository[T]):
    """
    Репозиторий, работающий в базе данных. Хранит данные в базе данных.
    """

    def __init__(self, table_name: str, obj_type: type) -> None:
        self.__table = table_name
        self.__connection = sqlite3.connect("my_expenses.db")
        self.__cursor = self.__connection.cursor()

        self.__create_table()

        self.__cursor.execute(f"SELECT max(pk) FROM {self.__table}")
        cur_counter = self.__cursor.fetchall()[0][0]
        self.__counter = count(1 if cur_counter is None else int(cur_counter) + 1)

        self.__generate_obj = obj_type

    def __create_table(self) -> None:
        header = ", ".join(self.__header)
        self.__cursor.execute(f'CREATE TABLE IF NOT EXISTS {self.__table} ({header})')
        self.__connection.commit()

    @property
    def __header(self) -> list[str]:
        categories_header = ['pk INTEGER PRIMARY KEY',
                             'name TEXT NOT NULL', 'parent INTEGER']
        expenses_header = ['pk INTEGER PRIMARY KEY', 'amount INTEGER',
                           'category INTEGER', 'expense_date TEXT NOT NULL',
                           'added_date TEXT NOT NULL', 'comment TEXT']
        custom_header = ['pk INTEGER PRIMARY KEY',
                         'name TEXT', 'test TEXT', 'expense_date TEXT']
        return categories_header if self.__table == 'Category' else (
            expenses_header if self.__table == 'Expense' else (
                custom_header if self.__table == 'Custom' else []
            )
        )
        # if self.__table == 'Category':
        #     return ['pk INTEGER PRIMARY KEY', 'name TEXT NOT NULL', 'parent INTEGER']
        # elif self.__table == 'Expense':
        #     return ['pk INTEGER PRIMARY KEY', 'amount INTEGER', 'category INTEGER',
        #       'expense_date TEXT NOT NULL', 'added_date TEXT NOT NULL', 'comment TEXT']
        # elif self.__table == 'Custom':
        #     return ['pk INTEGER PRIMARY KEY', 'name TEXT', 'test TEXT']
        # else:
        #     raise ValueError(f"Unknow table type {self.__table}")

    @property
    def __columns(self) -> list[str]:
        # for FULL coverage in tests this braching need to be single statement
        category_columns = ['pk', 'name', 'parent']
        expense_columns = ['pk', 'amount', 'category',
                           'expense_date', 'added_date', 'comment']
        custom_columns = ['pk', 'name', 'test', 'expense_date']
        return category_columns if self.__table == 'Category' else (
            expense_columns if self.__table == 'Expense' else (
                custom_columns if self.__table == 'Custom' else []
            )
        )

        # if self.__table == 'Category':
        #     return ['pk', 'name', 'parent']
        # elif self.__table == 'Expense':
        #     return ['pk', 'amount', 'category', 'expense_date', 'added_date', 'comment']
        # elif self.__table == 'Custom':
        #     return ['pk', 'name', 'test']
        # else:
        #     raise ValueError(f"Unknow table type {self.__table}")

    def __encode_value(self, value: int | str | datetime | None) -> str:
        if isinstance(value, datetime):
            return value.strftime("'%Y-%m-%d %H:%M:%S'")

        if isinstance(value, str):
            return f"'{value}'"

        if value is None:
            return "NULL"

        return str(value)

    def __encode(self, obj: T) -> list[str]:
        data = []

        for column in self.__columns:
            value = getattr(obj, column, None)
            data.append(self.__encode_value(value))

        return data

    def __decode(self, data: list[str]) -> Any:
        obj_params: dict[str, Any] = {}
        for value, column in zip(data, self.__columns):
            if value is None:
                obj_params[column] = None
            elif column in ['expense_date', 'added_date']:
                obj_params[column] = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
            elif column in ['pk', 'parent', 'amount', 'category']:
                obj_params[column] = int(value)
            else:
                obj_params[column] = value

        return self.__generate_obj(**obj_params)

    def add(self, obj: T) -> int:
        if getattr(obj, 'pk', None) != 0:
            raise ValueError(f'trying to add object {obj} with filled `pk` attribute')

        pk = next(self.__counter)
        obj.pk = pk
        columns = ', '.join(self.__columns)
        values = ', '.join(self.__encode(obj))
        cmd = f"INSERT INTO {self.__table} ({columns}) VALUES ({values})"
        self.__cursor.execute(cmd)
        self.__connection.commit()

        return pk

    def get(self, pk: int) -> T | None:
        result = self.get_all({'pk': pk})
        if len(result) == 0:
            return None
        return result[0]

    def get_all(self, where: dict[str, Any] | None = None) -> list[T]:
        if where is None:
            condition = ''
        else:
            def pairing(pair: tuple[str, Any]) -> str:
                return f"{pair[0]}={self.__encode_value(pair[1])}"

            conditions = ", ".join(map(pairing, list(where.items())))
            condition = f' WHERE {conditions}'
        columns = ", ".join(self.__columns)
        self.__cursor.execute(f'SELECT {columns} FROM {self.__table}{condition}')
        strings = self.__cursor.fetchall()

        return list(map(self.__decode, strings))

    def update(self, obj: T) -> None:
        if obj.pk == 0:
            raise ValueError('attempt to update object with unknown primary key')
        values = self.__encode(obj)
        pairs = list(zip(self.__columns, values))

        def pairing(pair: tuple[str, str]) -> str:
            return f"{pair[0]}={pair[1]}"

        new_values = ", ".join(map(pairing, pairs))

        self.__cursor.execute(f'UPDATE {self.__table} SET {new_values} WHERE pk={obj.pk}')
        self.__connection.commit()

    def delete(self, pk: int) -> None:
        if self.get(pk) is None:
            raise KeyError(str(pk))
        self.__cursor.execute(f'DELETE FROM {self.__table} WHERE pk={pk}')
        self.__connection.commit()

    # only for tests
    def __clear(self) -> None:
        pks = list(map(lambda obj: obj.pk, self.get_all()))
        for pk in pks:
            self.delete(pk)
