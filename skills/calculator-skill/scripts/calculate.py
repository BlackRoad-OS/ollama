#!/usr/bin/env python3
"""
Calculator script for performing mathematical operations.
Usage: python calculate.py <expression>
Example: python calculate.py "25 * 4"
"""
import sys
import re

def safe_eval(expression):
    """Safely evaluate a mathematical expression."""
    # Only allow numbers, operators, parentheses, and whitespace
    if not re.match(r'^[\d\s\+\-\*\/\.\(\)\%]+$', expression):
        raise ValueError(f"Invalid expression: {expression}")

    # Replace % with /100* for percentage calculations
    # e.g., "15% of 200" would be passed as "15/100*200"

    try:
        result = eval(expression)
        return result
    except Exception as e:
        raise ValueError(f"Could not evaluate: {e}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python calculate.py <expression>")
        print("Example: python calculate.py '25 * 4'")
        sys.exit(1)

    expression = ' '.join(sys.argv[1:])

    try:
        result = safe_eval(expression)
        print(f"{expression} = {result}")
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
