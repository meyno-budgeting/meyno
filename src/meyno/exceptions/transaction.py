class TransactionError(Exception):
    """Base exception for transaction-related errors."""


class TransactionNotFoundError(TransactionError):
    """Raised when a transaction could not be found"""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class TransactionConversionError(TransactionError):
    """Raised when a transaction is already a transfer"""

    def __init__(self) -> None:
        super().__init__("Transaction is already a transfer")


class TransferConversionError(TransactionError):
    """Raised when a transaction is already not a transfer"""

    def __init__(self) -> None:
        super().__init__("Transaction is already not a transfer")
