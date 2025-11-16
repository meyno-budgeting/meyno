
from bisect import insort
from tabulate import tabulate
from .transaction import Transaction

class Account:
    def __init__(self, name: str, transactions: list[Transaction] | None = None) -> None:
        self.name: str = name

        if transactions is None:
            transactions = []

        if not isinstance(transactions, list):
            raise TypeError("transactions must be a list of Transaction objects.")

        for tx in transactions:
            if not isinstance(tx, Transaction):
                raise TypeError("All items in transactions must be Transaction objects.")

        self.transactions: list[Transaction] = sorted(transactions, key=lambda t: t.date)
        self._id_map: dict[str, Transaction] = {tx.id: tx for tx in self.transactions}
       
    @property
    def balance(self) -> float:
        return sum(txn.amount for txn in self.transactions)
    
    def add_transaction(self, txn: Transaction) -> None:
        insort(self.transactions, txn, key=lambda t: t.date)
        self._id_map[txn.id] = txn
        
    def delete_transaction(self, id) -> None:
        txn = self.get_transaction(id=id)
        
        if txn is not None:
            self.transactions.remove(txn)
            del self._id_map[id]
        
        return

    def get_transaction(self, id) -> Transaction | None:
        return self._id_map.get(id, None)
    def __str__(self) -> str:
        # Display newest first
        display_list = self.transactions[::-1]

        headers = ["Date", "Payee", "Category", "Amount", "Memo"]
        rows = [[
            t.formattedDate(),
            t.payee,
            t.category,
            f"${t.amount:.2f}",
            t.memo
        ] for t in display_list]

        out = [
            f"Account: {self.name}",
            f"Balance: ${self.balance:.2f}\n",
            tabulate(rows, headers=headers, tablefmt="simple")
        ]

        return "\n".join(out)
    
    def __repr__(self) -> str:
        return f"Account({self.__dict__})"
    
    def __len__(self):
        return len(self.transactions)