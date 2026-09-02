class PayeeError(Exception):
    """Base exception for payee-related errors."""


class PayeeAlreadyExistsError(PayeeError):
    """Raised when a payee already exists."""

    def __init__(self, payee_name: str) -> None:
        self.payee_name = payee_name
        super().__init__(f"Payee already exists: {payee_name}")


class PayeeNameEmptyError(PayeeError):
    """Raised when a payee name is empty."""

    def __init__(self) -> None:
        super().__init__("Payee name cannot be empty.")


class PayeeNotFoundError(PayeeError):
    """Raised when a payee cannot be found."""

    def __init__(self, search_value: str | int) -> None:
        self.search_value = search_value
        super().__init__(f"Payee not found: {search_value}")
