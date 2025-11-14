
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

    def get_transaction(self, uuid) -> Transaction:
        
        return