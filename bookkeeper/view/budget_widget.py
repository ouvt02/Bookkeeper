'''Виджет бюджета'''
from __future__ import annotations
from typing import Any
from PySide6 import QtWidgets
from bookkeeper.view.bookkeeper_widget import BookkeeperWidget


class BudgetWidget(BookkeeperWidget):
    '''Класс, реализующий виджет бюджета'''
    def __init__(self) -> None:
        super().__init__()
        self.table = QtWidgets.QTableWidget()
        vert_layout = QtWidgets.QVBoxLayout()
        self.table.setRowCount(3)
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(['Сумма', 'Бюджет'])
        self.table.setVerticalHeaderLabels(['День', 'Неделя', 'Месяц'])
        self.table.cellChanged.connect(self.edit_budget)
        vert_layout.addWidget(self.table)
        self.setLayout(vert_layout)

    def fill_table(self, data: Any) -> None:
        '''Метод для заполнения виджета бюджета'''
        self.table.cellChanged.disconnect()
        self.table.setRowCount(3)
        for row_num, row in enumerate(data):
            for value_num, value in enumerate(row):
                self.table.setItem(row_num, value_num, QtWidgets.QTableWidgetItem(value))
        self.table.cellChanged.connect(self.edit_budget)

    def update_widget(self, data: dict[str, Any]) -> None:
        '''Метод для обновления виджета согласно изменению в данных'''
        if 'budget' in data:
            self.fill_table(data['budget'])

    def edit_budget(self, row: int) -> None:
        '''Метод для изменения бюджета через взаимодействие пользователя с виджетом'''
        if row == 0:
            period = 'day'
        elif row == 1:
            period = 'week'
        else:
            period = 'month'
        new_budget = self.table.item(row, 1)
        if new_budget is not None and self.presenter is not None:
            new_budget_str = new_budget.text()
            self.presenter.process("editBudget",
                                   {"period": period, 'budget': new_budget_str})
