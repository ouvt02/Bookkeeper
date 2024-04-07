from bookkeeper.repository.sqlite_repository import SqliteRepository

import pytest
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Custom():
    pk: int = 0
    name: str = None
    test: str = None
    expense_date: datetime = datetime.now()

    def __eq__(self, other):
        return other != None and self.pk == other.pk and self.name == other.name and self.test == other.test

@pytest.fixture
def custom_class():
    return Custom


@pytest.fixture
def repo():
    return SqliteRepository("Custom", Custom)


def test_crud(repo, custom_class):
    obj = custom_class()
    pk = repo.add(obj)
    assert obj.pk == pk
    assert repo.get(pk) == obj
    obj2 = custom_class()
    obj2.pk = pk
    repo.update(obj2)
    assert repo.get(pk) == obj2
    repo.delete(pk)
    assert repo.get(pk) is None
    repo._SqliteRepository__clear()


def test_cannot_add_with_pk(repo, custom_class):
    obj = custom_class()
    obj.pk = 1
    with pytest.raises(ValueError):
        repo.add(obj)
    repo._SqliteRepository__clear()

def test_cannot_add_without_pk(repo):
    with pytest.raises(ValueError):
        repo.add(0)
    repo._SqliteRepository__clear()

def test_cannot_delete_unexistent(repo):
    with pytest.raises(KeyError):
        repo.delete(1)
    repo._SqliteRepository__clear()

def test_cannot_update_without_pk(repo, custom_class):
    obj = custom_class()
    with pytest.raises(ValueError):
        repo.update(obj)
    repo._SqliteRepository__clear()

def test_get_all(repo, custom_class):
    objects = [custom_class() for i in range(5)]
    for o in objects:
        repo.add(o)
    assert repo.get_all() == objects
    repo._SqliteRepository__clear()

def test_get_all_with_condition(repo, custom_class):
    objects = []
    for i in range(5):
        o = custom_class()
        o.name = str(i)
        o.test = 'test'
        repo.add(o)
        objects.append(o)
    assert repo.get_all({'name': '0'}) == [objects[0]]
    assert repo.get_all({'test': 'test'}) == objects
    repo._SqliteRepository__clear()