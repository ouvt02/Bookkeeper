'''Presenter'''
from __future__ import annotations
from typing import Any
from dataclasses import asdict
from json import loads, dumps
from datetime import datetime, timedelta
from bookkeeper.models.category import Category
from bookkeeper.models.expense import Expense
from bookkeeper.repository.abstract_repository import AbstractRepository


class Presenter:
    '''Класс реализующий Presenter'''
    def __init__(self, cat_repo: AbstractRepository[Category],
                 exp_repo: AbstractRepository[Expense]) -> None:
        self.cat_repo = cat_repo
        self.exp_repo = exp_repo
        self.widgets: list[Any] = []

    def process(self, command: str, params: dict[str, Any]) -> None:
        '''Метод для обработки событий в виджетах'''
        try:
            if command == "addExpense":
                try:
                    cat = self.cat_repo.get_all({'name': params['category']})[0]
                except IndexError:
                    pass
                exp: Expense | None = Expense(int(params['amount']), cat.pk)
                if exp is not None:
                    self.exp_repo.add(exp)

            elif command == "editExpense":
                exp = self.exp_repo.get(int(params['pk']))
                exp_dict = asdict(exp)
                edited_column = list(params.keys())[1]

                if edited_column == "expense_date":
                    exp_dict[edited_column] = datetime.strptime(params[edited_column],
                                                                "%Y-%m-%d %H:%M:%S")
                elif edited_column == "amount":
                    exp_dict[edited_column] = int(params[edited_column])
                elif edited_column == "category":
                    try:
                        cat = self.cat_repo.get_all({'name': params[edited_column]})[0]
                    except IndexError:
                        pass
                    exp_dict[edited_column] = cat.pk
                else:
                    exp_dict[edited_column] = params[edited_column]

                new_exp = Expense(**exp_dict)
                self.exp_repo.update(new_exp)

            elif command == "deleteExpense":
                self.exp_repo.delete(int(params["pk"]))

            elif command == "addCategory":
                self.cat_repo.add(Category(name=params['name']))

            elif command == "addSubCategory":
                self.cat_repo.add(Category(name=params['name'],
                                           parent=int(params['parent'])))

            elif command == "editCategory":
                edited: Category | None = self.cat_repo.get(int(params['pk']))
                if edited is not None:
                    edited.name = params['name']
                    self.cat_repo.update(edited)

            elif command == "deleteCategory":
                self.delete_category(int(params['pk']))

            elif command == "editBudget":
                budget: dict[str, int] = self.try_get_budget()
                budget[params['period']] = int(params['budget'])
                with open("budget.json", "w", encoding='utf-8') as budget_file:
                    budget_file.write(dumps(budget))

        except (IndexError, ValueError, KeyError, UnboundLocalError):
            pass
        self.update_widgets()

    def delete_category(self, pk: int) -> None:
        '''Метод для удаления категории'''
        children = self.cat_repo.get_all({'parent': pk})
        for child in children:
            self.delete_category(child.pk)
        expenses = self.exp_repo.get_all({'category': pk})
        for exp in expenses:
            self.exp_repo.delete(exp.pk)
        self.cat_repo.delete(pk)

    def connect_widgets(self, *args: Any) -> None:
        '''Метод для подключения виджетов к Presenter'''
        self.widgets += list(args)
        for widget in self.widgets:
            widget.connect_presenter(self)

    def try_get_budget(self) -> dict[str, int]:
        '''Метод для получения бюджета из файла'''
        budget: dict[str, int] = {'day': 1000, 'week': 7000, 'month': 30000}
        try:
            with open("budget.json", "r", encoding='utf-8') as budget_file:
                result = loads(budget_file.read())
                for key in result:
                    if key in budget and isinstance(result[key], int):
                        budget[key] = result[key]

        except FileNotFoundError:
            with open("budget.json", "w", encoding='utf-8') as budget_file:
                budget_file.write(dumps(budget))

        return budget

    def update_widgets(self) -> None:
        '''Метод для обновления виджетов согласно изменениям в данных'''
        exp_info = sorted(self.exp_repo.get_all(),
                          key=lambda exp: exp.expense_date, reverse=True)
        cat_info = self.cat_repo.get_all()

        expenses_table = []
        for exp in exp_info:
            cat = self.cat_repo.get(exp.category)
            if cat is not None:
                expenses_table.append([
                    str(exp.pk), exp.expense_date.strftime("%Y-%m-%d %H:%M:%S"),
                    str(exp.amount), cat.name, exp.comment])

        cat_list = []
        cat_list_with_pk = []
        for cat in cat_info:
            cat_list.append(cat.name)
            cat_list_with_pk.append((cat.pk, cat.parent, cat.name))

        sums_and_budgets = []
        cur_day_sum = 0
        cur_week_sum = 0
        cur_month_sum = 0

        now = datetime.now()
        delta = timedelta(days=now.weekday(), hours=now.hour,
                          minutes=now.minute, seconds=now.second,
                          microseconds=now.microsecond)
        lateset_monday = now - delta
        for exp in exp_info:
            if exp.expense_date.month == now.month and \
               exp.expense_date.year == now.year:
                cur_month_sum += exp.amount

                if exp.expense_date.day == now.day:
                    cur_day_sum += exp.amount

            if now >= lateset_monday:
                cur_week_sum += exp.amount

        budget_info = self.try_get_budget()
        sums_and_budgets = [(str(cur_day_sum), str(budget_info['day'])),
                            (str(cur_week_sum), str(budget_info['week'])),
                            (str(cur_month_sum), str(budget_info['month']))]

        data = {'expenses_table': expenses_table, 'categories_list': cat_list,
                'categories_list_with_pk': cat_list_with_pk, 'budget': sums_and_budgets}

        for widget in self.widgets:
            widget.update_widget(data)
