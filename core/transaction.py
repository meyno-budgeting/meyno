
from datetime import datetime as dt, date as Date
import uuid

class Transaction:
    
    dateFormat = "%m/%d/%Y"
    
    def __init__(self, date: Date | str, payee: str = "", category: str = "Uncategorized", amount: float = 0.00, memo: str = "") -> None:
        # Parse or validate date
        if isinstance(date, str):
            parsed_date: Date = dt.strptime(date, Transaction.dateFormat).date()
        elif isinstance(date, Date):
            parsed_date = date
        else:
            raise TypeError(f"date must be a str or datetime.date, not {type(date).__name__}")

        self.date: Date = parsed_date
        self.payee: str = payee
        self.category: str = category
        self.amount: float = amount
        self.memo: str = memo
        self.id: str = str(uuid.uuid4())
    
    def formattedDate(self) -> str:
        return self.date.strftime(format=Transaction.dateFormat)
    
    def __str__(self) -> str:
        emptyStringStr = "\'\'"

        payeeStr = self.payee if self.payee else emptyStringStr
        categoryStr = self.category if self.category else emptyStringStr
        memoStr = self.memo if self.memo else emptyStringStr
        
        return f"Date: {self.formattedDate()} Payee: {payeeStr} Category: {categoryStr} Amount: ${self.amount:.2f} Memo: {memoStr}"

    def __repr__(self) -> str:
        return f"Transaction({self.__dict__})"
