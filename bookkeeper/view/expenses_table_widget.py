'''Виджет для отображения трат'''
from __future__ import annotations
from typing import Any
from PySide6 import QtWidgets
from bookkeeper.view.bookkeeper_widget import BookkeeperWidget


class ExpensesTableWidget(BookkeeperWidget):
    '''Класс, реализующий виджет для отображения трат'''
    def __init__(self) -> None:
        super().__init__()
        layout = QtWidgets.QVBoxLayout()
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(5)
        self.table.cellChanged.connect(self.edit_expense)
        self.table.setHorizontalHeaderLabels([
            'Pk', 'Дата', 'Сумма', 'Категория', 'Комментарий'])
        delete_button = QtWidgets.QPushButton("Удалить выбранное")
        delete_button.clicked.connect(self.delete_exp)
        self.table.hideColumn(0)
        layout.addWidget(self.table)
        layout.addWidget(delete_button)
        self.setLayout(layout)

    def fill_table(self, data: list[list[str]]) -> None:
        '''Метод для заполнения таблицы трат'''
        self.table.cellChanged.disconnect()
        self.table.setRowCount(len(data))
        for row_num, row in enumerate(data):
            for value_num, value in enumerate(row):
                self.table.setItem(row_num, value_num, QtWidgets.QTableWidgetItem(value))
        self.table.cellChanged.connect(self.edit_expense)

    def update_widget(self, data: dict[str, Any]) -> None:
        '''Метод для обновления отображаемых в виджете данных'''
        if 'expenses_table' in data:
            self.fill_table(data['expenses_table'])

    def edit_expense(self, row: int, column: int) -> None:
        '''Метод для изменения траты'''
        if column == 1:
            col_name = "expense_date"
        elif column == 2:
            col_name = "amount"
        elif column == 3:
            col_name = "category"
        elif column == 4:
            col_name = "comment"

        pk = self.table.item(row, 0)
        changed_item = self.table.item(row, column)
        if pk is not None and changed_item is not None and self.presenter is not None:
            pk_str = pk.text()
            item_data = changed_item.text()
            self.presenter.process("editExpense", {"pk": pk_str, col_name: item_data})

    def delete_exp(self) -> None:
        '''Метод для удаления траты'''
        current_row = self.table.currentRow()
        pk = self.table.item(current_row, 0)
        if pk is not None and self.presenter is not None:
            pk_str = pk.text()
            self.presenter.process("deleteExpense", {"pk": pk_str})
