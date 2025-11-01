from dataclasses import dataclass, field
import uuid

@dataclass
class Transaction:
    id: str = field(default_factory=lambda: str(uuid.uuid4()), init=False)
    date : str
    payee: str = ""
    category: str = "Uncategorized"
    amount: float = 0.00
    memo: str = ""

    # def __init__(self, date: str, payee: str = "", category: str = "Uncategorized", amount: float = 0.00, memo: str = "") -> None:
    #     self.date = date
    #     self.payee = payee
    #     self.category = category
    #     self.amount = amount
    #     self.memo = memo

