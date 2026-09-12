import uuid


class TransactionError(Exception):
    """Base exception for transaction-related errors."""


class TransactionNotFoundError(TransactionError):
    """Raised when a transaction could not be found"""

    def __init__(self, transaction_id: uuid.UUID) -> None:
        self.transaction_id = transaction_id
        super().__init__(f"Transaction not found: {transaction_id}")


class TransactionConversionError(TransactionError):
    """Raised when a transaction is already a transfer"""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class TransferConversionError(TransactionError):
    """Raised when a transaction is already not a transfer"""

    def __init__(self) -> None:
        super().__init__("Transaction is already not a transfer")


class TransferOtherSideNotFoundError(TransactionError):
    """Raised when a transaction is already not a transfer"""

    def __init__(self) -> None:
        super().__init__("Could not find other side of transfer")


class InvalidTransactionError(TransactionError):
    """Raised when a transaction or transfer is invalid after creating or updating"""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class InvalidTransferCreateError(TransactionError):
    """Raised when a TransferCreate has invalid data"""

    def __init__(self, message: str) -> None:
        super().__init__(message)
