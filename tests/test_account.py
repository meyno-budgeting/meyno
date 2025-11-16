import pytest
from core.transaction import Transaction
from core.account import Account


def test_default_constructor():
    acc = Account("Checking")

    assert acc.name == "Checking"
    assert len(acc) == 0
    assert acc.balance == 0
    assert acc.transactions == []
    assert acc._id_map == {}


def test_parameterized_constructor():
    t1 = Transaction("1/3/2025")  # later
    t2 = Transaction("1/1/2025")  # earlier
    t3 = Transaction("1/2/2025")

    acc = Account("Checking", [t1, t2, t3])

    # Ensure sorted by date
    assert acc.transactions == [t2, t3, t1]

    # Ensure ID map matches
    for tx in [t1, t2, t3]:
        assert tx.id in acc._id_map


def test_add_transaction():
    acc = Account("Checking")

    t1 = Transaction("1/5/2025")
    t2 = Transaction("1/1/2025")
    t3 = Transaction("1/3/2025")

    acc.add_transaction(t1)
    acc.add_transaction(t2)
    acc.add_transaction(t3)

    assert acc.transactions == [t2, t3, t1]
    assert acc._id_map[t1.id] == t1
    assert acc._id_map[t2.id] == t2
    assert acc._id_map[t3.id] == t3


def test_delete_transaction():
    t1 = Transaction("1/1/2025")
    t2 = Transaction("1/2/2025")

    acc = Account("Checking", [t1, t2])

    acc.delete_transaction(t1.id)

    assert len(acc) == 1
    assert acc.transactions == [t2]
    assert t1.id not in acc._id_map


def test_balance_property():
    t1 = Transaction("1/1/2025", amount=50)
    t2 = Transaction("1/2/2025", amount=-20)
    t3 = Transaction("1/3/2025", amount=100)

    acc = Account("Checking", [t1, t2, t3])

    assert acc.balance == 130  # 50 - 20 + 100
