# Specs for Assignment1 calculator_cfg.py

## Overview
This calculator implements a small expression language described by `grammar.lark`. The program:
1. Parses an input expression (string) with Lark into a parse tree (AST).
2. Evaluates the AST recursively to produce a numeric result.

Files required:
- `grammar.lark` — the Lark grammar (unambiguous; enforces operator precedence and associativity)
- `calculator_cfg.py` — parser + AST evaluator + CLI
- `specs.md` — this file (detailed specification)

---

## Grammar Summary and Operator Precedence
The grammar implements the following precedence (highest → lowest):

1. **Exponentiation (`^`)**  
   - Right-associative.  
   - Example: `2^3^2` → parsed as `2^(3^2)` → evaluates to `512`.

2. **Unary negation (`-`)**  
   - Applies *after* exponentiation.  
   - Example: `-3^2` → parsed as `-(3^2)` → evaluates to `-9`.  
   - Multiple unary minuses are supported: `--1` → `1`.

3. **Multiplication (`*`)**  
   - Left-associative.

4. **Addition and subtraction (`+`, `-`)**  
   - Binary forms are left-associative.

5. **Primary forms (atoms):**  
   - Numbers  
   - Parenthesized expressions `( ... )`  
   - Logarithms: `log <expr> base <expr>` (with integer-log-friendly evaluation)

---

## Grammar Decisions and Unambiguity
- The original ambiguous grammar (`exp -> exp '+' exp` etc.) was restructured into distinct precedence levels:  
  - `add`, `mul`, `unary`, `pow`, `atom`.  
- Right-associativity for exponentiation is handled with:  
  ```lark
  pow: atom "^" pow | atom
