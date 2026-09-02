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
