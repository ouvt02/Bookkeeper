'''Виджет для добавления трат'''
from __future__ import annotations
from typing import Any
from PySide6 import QtWidgets
from bookkeeper.view.bookkeeper_widget import BookkeeperWidget
from bookkeeper.view.edit_category_widget import EditCategoryWidget


class AddExpenseWidget(BookkeeperWidget):
    '''Класс, реализующий виджет для добавления трат'''
    def __init__(self) -> None:
        super().__init__()
        self.edit_category_widget = EditCategoryWidget()
        layout = QtWidgets.QVBoxLayout()

        first_row = QtWidgets.QWidget()
        hor_layout1 = QtWidgets.QHBoxLayout()
        hor_layout1.addWidget(QtWidgets.QLabel('Сумма'))
        self.input: QtWidgets.QLineEdit = QtWidgets.QLineEdit('0')
        hor_layout1.addWidget(self.input)
        first_row.setLayout(hor_layout1)

        second_row = QtWidgets.QWidget()
        hor_layout2 = QtWidgets.QHBoxLayout()
        hor_layout2.addWidget(QtWidgets.QLabel('Категория'))
        self.combo_box = QtWidgets.QComboBox()
        hor_layout2.addWidget(self.combo_box)
        edit_button = QtWidgets.QPushButton('Редактировать')
        edit_button.clicked.connect(self.edit_category_widget.show)
        hor_layout2.addWidget(edit_button)
        second_row.setLayout(hor_layout2)

        third_row = QtWidgets.QWidget()
        hor_layout3 = QtWidgets.QHBoxLayout()
        self.button_add = QtWidgets.QPushButton('Добавить')
        self.button_add.clicked.connect(self.add_expense)
        hor_layout3.addWidget(self.button_add)
        third_row.setLayout(hor_layout3)

        layout.addWidget(first_row)
        layout.addWidget(second_row)
        layout.addWidget(third_row)

        self.setLayout(layout)

    def set_available_categories(self, categories: list[str]) -> None:
        '''Метод для заполнения возможных для выбора категорий'''
        self.combo_box.clear()
        self.combo_box.addItems(categories)

    def add_expense(self) -> None:
        '''Метод для добавления траты'''
        amount = self.input.text()
        category = self.combo_box.currentText()
        if self.presenter is not None:
            self.presenter.process("addExpense", {'amount': amount, 'category': category})

    def update_widget(self, data: dict[str, Any]) -> None:
        '''Метод для обновления виджета согласно изменению в данных'''
        if 'categories_list' in data:
            self.set_available_categories(data['categories_list'])
