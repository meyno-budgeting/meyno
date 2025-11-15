
from datetime import datetime as dt, date as Date

from core.transaction import Transaction
from core.account import Account

def main():
    txns: list[Transaction] = []
    txns.append(Transaction(date=dt.today().date(), amount=63.29, payee="Walmart",memo="Metroid Prime 4"))
    txns.append(Transaction(date=dt.today().date(), amount=81.67, payee="Utilities"))
    txns.append(Transaction(date="12/5/2025", amount=169.32, memo="Groceries"))


    # print(str(txns[0])+'\n\n')

    a = Account(name="Account", transactions=txns)
    txn_to_add = Transaction(date="12/04/2025",payee="Nintendo", amount=9.99*1.055, memo="MP4 Switch 2 Upgrade")
    a.add_transaction(txn_to_add)
    print(a)

    # id = a.transactions[0].id
    # txn = a.get_transaction(id=id)
    # print(txn)
    
    # print(a.transactions)


if __name__ == "__main__":
    main()
