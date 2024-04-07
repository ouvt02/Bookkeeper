"""
Простой тестовый скрипт для терминала
"""

from bookkeeper.models.category import Category
from bookkeeper.models.expense import Expense
from bookkeeper.repository.sqlite_repository import SqliteRepository
from bookkeeper.utils import read_tree

cat_repo = SqliteRepository[Category]('Category', Category)
exp_repo = SqliteRepository[Expense]('Expense', Expense)

cats = '''
продукты
    мясо
        сырое мясо
        мясные продукты
    сладости
книги
одежда
'''.splitlines()

if len(cat_repo.get_all()) == 0:
    Category.create_from_tree(read_tree(cats), cat_repo)

while True:
    try:
        cmd = input('$> ')
    except EOFError:
        break
    if not cmd:
        continue
    if cmd == 'категории':
        print(*cat_repo.get_all(), sep='\n')
    elif cmd == 'расходы':
        print(*exp_repo.get_all(), sep='\n')
    # elif cmd.startswith('удалить'):
    #     args = cmd.split(' ')
    #     exp_repo.delete(int(args[1]))
    # elif cmd.startswith('получить'):
    #     args = cmd.split(' ')
    #     print(exp_repo.get(int(args[1])))
    # elif cmd.startswith('изменить'):
    #     args = cmd.split(' ')
    #     obj = cat_repo.get_all({'name': args[1]})[0]
    #     obj.name = args[2]
    #     cat_repo.update(obj)
    elif cmd[0].isdecimal():
        amount, name = cmd.split(maxsplit=1)
        try:
            cat = cat_repo.get_all({'name': name})[0]
        except IndexError:
            print(f'категория {name} не найдена')
            continue
        exp = Expense(int(amount), cat.pk)
        exp_repo.add(exp)
        print(exp)
