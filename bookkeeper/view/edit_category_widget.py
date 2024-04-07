'''Виджет для изменения категорий'''
from __future__ import annotations
from typing import Any
from PySide6 import QtWidgets
from bookkeeper.view.bookkeeper_widget import BookkeeperWidget


class EditCategoryWidget(BookkeeperWidget):
    '''Класс, реализующий виджет для изменения категорий'''
    def __init__(self) -> None:
        super().__init__()
        self.tree = QtWidgets.QTreeWidget()
        layout = QtWidgets.QVBoxLayout()

        self.tree.setColumnCount(2)
        self.tree.setHeaderLabels(['Categories', 'pk'])
        self.tree.hideColumn(1)
        self.resize(500, 500)
        self.tree.setHeaderHidden(True)

        add_button = QtWidgets.QPushButton("Добавить категорию")
        delete_button = QtWidgets.QPushButton("Удалить выбранную категорию")
        add_child_button = QtWidgets.QPushButton("Добавить подкатегорию")
        edit_button = QtWidgets.QPushButton("Переименовать")

        add_button.clicked.connect(self.add_category)
        delete_button.clicked.connect(self.delete_category)
        add_child_button.clicked.connect(self.add_sub_category)
        edit_button.clicked.connect(self.edit_category)

        layout.addWidget(self.tree)
        self.add_line = QtWidgets.QLineEdit("Имя категории")
        layout.addWidget(self.add_line)
        layout.addWidget(add_button)
        layout.addWidget(add_child_button)
        layout.addWidget(edit_button)
        layout.addWidget(delete_button)
        self.setLayout(layout)

    def update_widget(self, data: dict[str, Any]) -> None:
        '''Метод для обновления виджета согласно изменению в данных'''
        if 'categories_list_with_pk' in data:
            self.tree.clear()
            self.fill_tree(data['categories_list_with_pk'])

    def fill_tree(self, data: list[tuple[int, int, str]],
                  parent: QtWidgets.QTreeWidgetItem | None = None,
                  parent_pk: int | None = None) -> None:
        '''Метод для заполнения дерева каталогов'''
        children = filter(lambda tup: tup[1] == parent_pk, data)
        for item in children:
            child = QtWidgets.QTreeWidgetItem([item[2], str(item[0])])
            if parent is None:
                self.tree.addTopLevelItem(child)
            else:
                parent.addChild(child)
            self.fill_tree(data, child, item[0])

    def delete_category(self) -> None:
        '''Метод для удаления категории'''
        item = self.tree.currentItem()
        if item is not None and self.presenter is not None:
            self.presenter.process("deleteCategory", {"pk": int(item.data(1, 0))})

    def add_category(self) -> None:
        '''Метод для добавления категории'''
        name = self.add_line.text()
        if self.presenter is not None:
            self.presenter.process("addCategory", {'name': name})

    def add_sub_category(self) -> None:
        '''Метод для добавления подкатегории'''
        name = self.add_line.text()
        cur_item = self.tree.currentItem()
        if cur_item is not None and self.presenter is not None:
            parent = int(cur_item.data(1, 0))
            self.presenter.process("addSubCategory", {'name': name, 'parent': parent})

    def edit_category(self) -> None:
        '''Метод для изменения категории'''
        new_name = self.add_line.text()
        cur_item = self.tree.currentItem()
        if cur_item is not None and self.presenter is not None:
            current = int(cur_item.data(1, 0))
            self.presenter.process("editCategory", {'name': new_name, 'pk': current})
