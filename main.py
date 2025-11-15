
from datetime import datetime as dt, date as Date

from core.transaction import Transaction
from core.account import Account

def main():
    txns: list[Transaction] = []
    txns.append(Transaction(date=dt.today().date(), amount=73.83))
    txns.append(Transaction(date=dt.today().date(), amount=81.67, payee="Utilities"))
    txns.append(Transaction(date=dt.today().date(), amount=169.32, memo="Groceries"))


    print(str(txns[0])+'\n\n')

    a = Account(name="Account", transactions=txns)
    print(a)

    # id = a.transactions[0].id
    # txn = a.get_transaction(id=id)
    # print(txn)
    
    # print(a.transactions)


if __name__ == "__main__":
    main()
