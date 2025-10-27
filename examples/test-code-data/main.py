#!/usr/bin/env python3
"""
Main module for the test application
"""
import os
import sys
from utils import calculate_sum, format_output
from models import User, Product


def main():
    """Main entry point"""
    user = User("Alice", "alice@example.com")
    product = Product("Widget", 29.99)

    total = calculate_sum([10, 20, 30])
    output = format_output(user.name, total)

    print(output)
    return 0


def initialize_app():
    """Initialize application settings"""
    config = {
        'debug': True,
        'log_level': 'INFO'
    }
    return config


if __name__ == "__main__":
    sys.exit(main())
