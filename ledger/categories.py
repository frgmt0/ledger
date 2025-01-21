"""
Categories enum for the ledger application.
"""
from enum import Enum

class Category(str, Enum):
    """Transaction categories."""
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
