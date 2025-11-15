
from tabulate import tabulate
from .transaction import Transaction

class Account:
    def __init__(self, name: str, transactions: list[Transaction]=[]) -> None:
       self.name = name
       self.transactions = transactions[:]
       
    @property
    def balance(self) -> float:
        return sum(txn.amount for txn in self.transactions)
    
    def add_transaction(self, txn: Transaction) -> None:
        self.transactions.append(txn)

    def get_transaction(self, id) -> Transaction | None:
        for txn in self.transactions:
            if txn.id == id:
                return txn
        return

    def __str__(self):
        table_headers = ["Date", "Payee", "Category", "Amount", "Memo"]
        table_data = [[t.formattedDate(), t.payee, t.category, f"${t.amount:.2f}", t.memo] for t in self.transactions]

        out = [
            f"Account: {self.name}",
            f"Balance: ${self.balance:.2f}\n",
            tabulate(table_data, headers=table_headers, tablefmt="simple")
        ]

        return "\n".join(out)
    
    def __repr__(self) -> str:
        return f"Account({self.__dict__})"