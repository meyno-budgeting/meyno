class AccountError(Exception):
    """Base exception for account-related errors."""


class AccountAlreadyExistsError(AccountError):
    """Raised when an account already exists."""

    def __init__(self, account_name: str) -> None:
        self.account_name = account_name
        super().__init__(f"Account already exists: {account_name}")


class AccountNameEmptyError(AccountError):
    """Raised when an account name is empty."""

    def __init__(self) -> None:
        super().__init__("Account name cannot be empty.")


class AccountNotFoundError(AccountError):
    """Raised when an account cannot be found."""

    def __init__(self, account_id: int) -> None:
        self.account_id = account_id
        super().__init__(f"Account not found: {account_id}")
