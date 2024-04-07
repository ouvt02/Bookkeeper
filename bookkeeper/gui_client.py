'''Графический клиент'''
import sys
from PySide6 import QtWidgets
from bookkeeper.models.category import Category
from bookkeeper.models.expense import Expense
from bookkeeper.repository.sqlite_repository import SqliteRepository
from bookkeeper.view.presenter import Presenter
from bookkeeper.view.application import Application

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    cat_repo = SqliteRepository[Category]('Category', Category)
    exp_repo = SqliteRepository[Expense]('Expense', Expense)
    presenter = Presenter(cat_repo, exp_repo)

    window = Application()
    window.show()

    presenter.connect_widgets(window.add_expense, window.expenses_table,
                              window.add_expense.edit_category_widget, window.budget)
    presenter.update_widgets()

    sys.exit(app.exec())
