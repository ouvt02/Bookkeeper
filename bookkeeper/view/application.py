'''Приложение'''
from __future__ import annotations
from PySide6 import QtWidgets
from bookkeeper.view.add_expense_widget import AddExpenseWidget
from bookkeeper.view.expenses_table_widget import ExpensesTableWidget
from bookkeeper.view.budget_widget import BudgetWidget


class Application(QtWidgets.QWidget):
    '''Класс, реализующий приложение'''
    def __init__(self) -> None:
        super().__init__()

        vert_layout = QtWidgets.QVBoxLayout()

        self.add_expense = AddExpenseWidget()
        self.expenses_table = ExpensesTableWidget()
        self.budget = BudgetWidget()

        vert_layout.addWidget(self.expenses_table)
        vert_layout.addWidget(self.budget)
        vert_layout.addWidget(self.add_expense)

        self.setLayout(vert_layout)
        self.resize(800, 800)
