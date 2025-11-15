
from tabulate import tabulate
from .transaction import Transaction

class Account:
    def __init__(self, name: str, transactions: list[Transaction]=[]) -> None:
       self.name: str = name
       self.transactions: list[Transaction] = transactions[:]
       self._id_map: dict[str, Transaction] = {tx.id: tx for tx in self.transactions}
       
    @property
    def balance(self) -> float:
        return sum(txn.amount for txn in self.transactions)
    
    def add_transaction(self, txn: Transaction) -> None:
        self.transactions.append(txn)
        self._id_map[txn.id] = txn
        
    def delete_transaction(self, id) -> None:
        txn = self.get_transaction(id=id)
        
        if txn is not None:
            self.transactions.remove(txn)
            del self._id_map[id]
        
        return

    def get_transaction(self, id) -> Transaction | None:
        return self._id_map.get(id, None)

    def __str__(self):
        sorted_transactions = sorted(self.transactions, key=lambda t: t.date.isoformat(), reverse=True)
        table_headers = ["Date", "Payee", "Category", "Amount", "Memo"]
        table_data = [[t.formattedDate(), t.payee, t.category, f"${t.amount:.2f}", t.memo] for t in sorted_transactions]

        out = [
            f"Account: {self.name}",
            f"Balance: ${self.balance:.2f}\n",
            tabulate(table_data, headers=table_headers, tablefmt="simple")
        ]

        return "\n".join(out)
    
    def __repr__(self) -> str:
        return f"Account({self.__dict__})"