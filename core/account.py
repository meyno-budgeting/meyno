
from .transaction import Transaction

class Account:
    def __init__(self, name: str, balance: float, transactions: list[Transaction]=[]) -> None:
       self.name = name
       self.balance = balance
       self.transactions = transactions
       
    
       