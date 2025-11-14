
from datetime import datetime as dt, date as Date

from core.transaction import Transaction
from core.account import Account

def main():
    txns = []
    a = Account("Hello", transactions=txns)
    txns.append(Transaction(dt.today().date(), amount=73.83))

    # t1 = Transaction(dt.today(), amount=73.83)
    # a.add_transaction(Transaction(dt.today(), amount=73.83))

    print(a.name)
    print(a.balance)


if __name__ == "__main__":
    main()
