#!/usr/bin/env python3
"""
Calculator using Lark parser generator
Implements a calculator with proper operator precedence and associativity
"""

import sys
import math
from lark import Lark, Transformer, v_args

# Load grammar from file
with open('grammar.lark', 'r') as f:
    grammar = f.read()

# Create parser
parser = Lark(grammar, parser='lalr')


@v_args(inline=True)
class CalculateTree(Transformer):
    """
    Transformer that converts parse tree to AST and evaluates expressions.
    Each method corresponds to a rule in the grammar.
    """
    
    def number(self, n):
        """Convert number token to float"""
        return float(n)
    
    def add(self, left, right):
        """Addition operator"""
        return left + right
    
    def sub(self, left, right):
        """Subtraction operator"""
        return left - right
    
    def mul(self, left, right):
        """Multiplication operator"""
        return left * right
    
    def exp(self, base, exponent):
        """Exponentiation operator (right-associative)"""
        return base ** exponent
    
    def neg(self, value):
        """Unary negation operator"""
        return -value
    
    def logarithm(self, value, base):
        """Logarithm with specified base"""
        return math.log(value, base)


def calculate(expression):
    """
    Parse and evaluate a mathematical expression.
    
    Args:
        expression: String containing the mathematical expression
        
    Returns:
        The numerical result of evaluating the expression
    """
    # Parse the expression to create parse tree
    tree = parser.parse(expression)
    
    # Transform parse tree to compute result
    result = CalculateTree().transform(tree)
    
    return result


def main():
    """
    Main function to handle command-line input.
    Usage: python calculator_cfg.py "expression"
    """
    if len(sys.argv) != 2:
        print("Usage: python calculator_cfg.py \"expression\"")
        sys.exit(1)
    
    expression = sys.argv[1]
    
    try:
        result = calculate(expression)
        # Format output: if integer, show as int; otherwise show as float
        if result == int(result):
            print(int(result))
        else:
            print(result)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
