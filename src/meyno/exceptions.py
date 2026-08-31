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
    """Raised when an category already exists."""

    def __init__(self, category_name: str) -> None:
        self.category_name = category_name
        super().__init__(f"Category already exists: {category_name}")


class CategoryNameEmptyError(CategoryError):
    """Raised when an category name is empty."""

    def __init__(self) -> None:
        super().__init__("Category name cannot be empty.")


class CategoryNotFoundError(CategoryError):
    """Raised when an category cannot be found."""

    def __init__(self, search_value: str | int) -> None:
        self.search_value = search_value
        super().__init__(f"Category not found: {search_value}")
