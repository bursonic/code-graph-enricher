"""
Data models for the application
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class User:
    """User model"""
    name: str
    email: str
    age: Optional[int] = None

    def is_adult(self) -> bool:
        """Check if user is adult"""
        return self.age and self.age >= 18

    def get_display_name(self) -> str:
        """Get formatted display name"""
        return f"{self.name} ({self.email})"


@dataclass
class Product:
    """Product model"""
    name: str
    price: float
    quantity: int = 1

    def calculate_total(self) -> float:
        """Calculate total price"""
        return self.price * self.quantity

    def apply_discount(self, percentage: float) -> float:
        """Apply discount to price"""
        discount = self.price * (percentage / 100)
        return self.price - discount


class ShoppingCart:
    """Shopping cart to hold products"""

    def __init__(self):
        self.items = []

    def add_item(self, product: Product):
        """Add product to cart"""
        self.items.append(product)

    def remove_item(self, product: Product):
        """Remove product from cart"""
        self.items.remove(product)

    def get_total(self) -> float:
        """Calculate total cart value"""
        return sum(item.calculate_total() for item in self.items)
