"""
Predefined transaction categories.
"""
from enum import Enum
from typing import Optional, Set

class Category(Enum):
    FOOD = "Food"
    HOUSING = "Housing"
    TRANSPORTATION = "Transportation"
    UTILITIES = "Utilities"
    HEALTHCARE = "Healthcare"
    ENTERTAINMENT = "Entertainment"
    SHOPPING = "Shopping"
    EDUCATION = "Education"
    INCOME = "Income"
    OTHER = "Other"

    @classmethod
    def values(cls) -> Set[str]:
        return {c.value for c in cls}

    @classmethod
    def get_category(cls, value: str) -> Optional['Category']:
        try:
            return cls(value)
        except ValueError:
            return None
