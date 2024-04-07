'''Родительский класс всех виджетов'''
from __future__ import annotations
from typing import Any
from PySide6 import QtWidgets
from bookkeeper.view.presenter import Presenter


class BookkeeperWidget(QtWidgets.QWidget):
    '''Класс, реализующий родительский для всех виджетов класс'''
    def __init__(self) -> None:
        super().__init__()
        self.presenter: Presenter | None = None

    def connect_presenter(self, presenter: Presenter) -> None:
        '''Метод для подключения Presenter к виджету'''
        self.presenter = presenter

    def update_widget(self, data: dict[str, Any]) -> None:
        '''Метод для обновления виджета согласно изменениям в данных'''
        pass
