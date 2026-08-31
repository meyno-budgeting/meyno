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

    def __init__(self, search_value: str | int) -> None:
        self.search_value = search_value
        super().__init__(f"Account not found: {search_value}")


class CategoryError(Exception):
    """Base exception for category-related errors."""


class CategoryAlreadyExistsError(CategoryError):
    """Raised when a category already exists."""

    def __init__(self, category_name: str) -> None:
        self.category_name = category_name
        super().__init__(f"Category already exists: {category_name}")


class CategoryNameEmptyError(CategoryError):
    """Raised when a category name is empty."""

    def __init__(self) -> None:
        super().__init__("Category name cannot be empty.")


class CategoryNotFoundError(CategoryError):
    """Raised when a category cannot be found."""

    def __init__(self, search_value: str | int) -> None:
        self.search_value = search_value
        super().__init__(f"Category not found: {search_value}")


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
