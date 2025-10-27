"""
Utility functions for the application
"""
from typing import List, Any


def calculate_sum(numbers: List[int]) -> int:
    """Calculate sum of numbers"""
    return sum(numbers)


def calculate_average(numbers: List[int]) -> float:
    """Calculate average of numbers"""
    if not numbers:
        return 0.0
    return sum(numbers) / len(numbers)


def format_output(name: str, value: Any) -> str:
    """Format output string"""
    return f"{name}: {value}"


class DataProcessor:
    """Process data with various transformations"""

    def __init__(self, data: List[Any]):
        self.data = data

    def filter_data(self, condition):
        """Filter data based on condition"""
        return [item for item in self.data if condition(item)]

    def transform_data(self, func):
        """Transform data using function"""
        return [func(item) for item in self.data]
