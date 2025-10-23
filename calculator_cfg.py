#!/usr/bin/env python3
"""
calculator_cfg.py

Usage:
    python calculator_cfg.py "1+2*3"

This script:
  1) Loads grammar.lark and builds a Lark parser.
  2) Parses the input expression into a Lark parse tree (AST).
  3) Recursively evaluates the AST to compute the numeric result.

Notes on design:
  - Exponentiation is right-associative (2^3^2 = 2^(3^2)).
  - Unary minus binds after exponentiation, so -3^2 = -(3^2).
  - Binary + and - are left-associative; * binds tighter than +/-
  - "log <n> base <b>" computes integer logarithm (rounded when necessary).
"""

import sys
from lark import Lark, Tree, Token
import math
import os

# Load grammar from the local file grammar.lark (must be in same directory)
_THIS_DIR = os.path.dirname(__file__) or "."
_GRAMMAR_PATH = os.path.join(_THIS_DIR, "grammar.lark")

with open(_GRAMMAR_PATH, "r", encoding="utf-8") as f:
    GRAMMAR = f.read()

parser = Lark(GRAMMAR, start="start", parser="lalr", propagate_positions=False, maybe_placeholders=False)

# -----------------------
# AST evaluator
# -----------------------
def evaluate(tree):
    """
    Recursively evaluate a Lark parse Tree or Token.
    We expect tree to be a Tree produced by Lark with rule names matching the grammar.
    """
    if isinstance(tree, Token):
        # NUMBER token
        if tree.type == "NUMBER":
            # Accept integers and floats in NUMBER token; convert to int if integer-valued
            s = str(tree)
            if "." in s or "e" in s or "E" in s:
                return float(s)
            else:
                # try int
                try:
                    return int(s)
                except ValueError:
                    return float(s)
        else:
            raise ValueError(f"Unexpected token type: {tree.type}")

    if not isinstance(tree, Tree):
        raise ValueError("evaluate expects a lark.Tree or lark.Token")

    op = tree.data
    children = tree.children

    if op == "start":
        return evaluate(children[0])

    if op == "number":
        # child is a Token(NUMBER)
        return evaluate(children[0])

    if op == "add":
        left = evaluate(children[0])
        right = evaluate(children[1])
        return left + right

    if op == "sub":
        left = evaluate(children[0])
        right = evaluate(children[1])
        return left - right

    if op == "mul":
        left = evaluate(children[0])
        right = evaluate(children[1])
        return left * right

    if op == "pow":
        base = evaluate(children[0])
        exponent = evaluate(children[1])
        # Use Python's pow (handles floats and ints)
        return base ** exponent

    if op == "neg":
        val = evaluate(children[0])
        return -val

    if op == "log":
        # children: [value_tree, base_tree]
        value = evaluate(children[0])
        base = evaluate(children[1])

        # Defensive checks
        if base == 1 or base == 0:
            raise ValueError("log base must not be 0 or 1")
        if value <= 0:
            raise ValueError("log of non-positive value is undefined")

        # Try to return an exact integer when appropriate (e.g., log 8 base 2 -> 3)
        # Otherwise compute using math.log and round to nearest integer when close to integer,
        # else return a floating point value.
        # We first attempt integer logarithm if value and base are integers.
        try:
            vi = int(value)
            bi = int(base)
            if vi == value and bi == base and vi > 0 and bi > 1:
                # check exact power: find k such that base^k == value
                k = 0
                cur = 1
                while cur < vi:
                    cur *= bi
                    k += 1
                if cur == vi:
                    return k
                # not exact; fall through to float computation
        except Exception:
            pass

        # general float result
        res = math.log(value, base)
        # if nearly integer, return integer
        if abs(res - round(res)) < 1e-9:
            return int(round(res))
        return res

    # Any parentheses produce a subtree; grammar ensures grouped expr becomes a subtree
    # Unknown rule
    raise NotImplementedError(f"Evaluation for tree node '{op}' not implemented")


def parse_to_ast(expr_str: str):
    """
    Parse the given expression string into a Lark parse tree (AST).
    Returns the Tree object produced by Lark.
    """
    return parser.parse(expr_str)


# -----------------------
# Command-line interface
# -----------------------
def main():
    if len(sys.argv) < 2:
        print("Usage: python calculator_cfg.py \"EXPR\"")
        print("Example: python calculator_cfg.py \"2^3^2\"")
        sys.exit(1)

    expr = sys.argv[1]
    try:
        ast = parse_to_ast(expr)
    except Exception as e:
        print("Parse error:", e)
        sys.exit(2)

    try:
        result = evaluate(ast)
    except Exception as e:
        print("Evaluation error:", e)
        sys.exit(3)

    # Print using a compact representation: integers printed as ints
    if isinstance(result, float) and result.is_integer():
        result = int(result)
    print(result)


if __name__ == "__main__":
    main()
