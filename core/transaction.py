
from datetime import datetime as dt, date as Date
import uuid

class Transaction:
    
    # outputDateFormat = 
    
    def __init__(self, date: dt | str, payee: str = "", category: str = "Uncategorized", amount: float = 0.00, memo: str = "") -> None:
        self.date = date
        self.payee = payee
        self.category = category
        self.amount = amount
        self.memo = memo
        self.id = str(uuid.uuid4())
    
        if isinstance(self.date, str):
            self.date = self._parse_date(self.date)
        elif not isinstance(self.date, Date):
            raise TypeError(f"date must be a str or datetime.date, not {type(self.date).__name__}")
            
    def _parse_date(self, date_str: str) -> Date:
        formats = ("%Y-%m-%d", "%m/%d/%Y", "%b %d, %Y")
        for fmt in formats:
            try:
                return dt.strptime(date_str, fmt).date()
            except ValueError:
                continue
        raise ValueError(f"Unsupported date format: {date_str}")
    
    def __str__(self) -> str:
        fields = {k: v for k, v in self.__dict__.items() if k != "id"}
        return str(fields)

    def __repr__(self) -> str:
        return f"Transaction({self.__dict__})"
