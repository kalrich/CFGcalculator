# Programming Assignment 1 - Calculator

This is a complete implementation of a calculator using the Lark parser generator for PL 2025.

## Files Included

- **calculator_cfg.py** - Main Python program
- **grammar.lark** - Lark grammar specification
- **specs.md** - Detailed implementation specifications
- **README.md** - This file

## Setup

### Install Dependencies

```bash
pip install lark-parser
```

Or with a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install lark-parser
```

## Usage

```bash
python calculator_cfg.py "expression"
```

### Examples

```bash
python calculator_cfg.py "1+2*3"
# Output: 7

python calculator_cfg.py "2^3^2"
# Output: 512

python calculator_cfg.py "log 8 base 2"
# Output: 3

python calculator_cfg.py "-3^2"
# Output: -9
```

## Supported Operations

- **Addition**: `+`
- **Subtraction**: `-` (binary)
- **Multiplication**: `*`
- **Exponentiation**: `^` (right-associative)
- **Unary Negation**: `-` (unary)
- **Logarithm**: `log value base base`
- **Parentheses**: `( )`

## Operator Precedence (High to Low)

1. Parentheses and Numbers
2. Logarithm (`log base`)
3. Exponentiation (`^`) - right-associative
4. Unary Negation (`-`)
5. Multiplication (`*`)
6. Addition/Subtraction (`+`, `-`)

## Test Cases

All required test cases pass:

| Expression | Result |
|------------|--------|
| `1+2*3` | 7 |
| `2-(4+2)` | -4 |
| `(3+2)*2` | 10 |
| `--1` | 1 |
| `2^3^2` | 512 |
| `2^3+1` | 9 |
| `2^3*2` | 16 |
| `log 8 base 2` | 3 |
| `log 8 base 2 + 1` | 4 |
| `-3^2` | -9 |

## Implementation Details

See `specs.md` for comprehensive implementation specifications including:
- Grammar design decisions
- Code structure and methods
- Order of operations explanation
- Testing results
- Design rationale

## Notes

- The calculator evaluates expressions in a single pass
- Operator precedence is enforced through grammar structure
- The implementation uses the LALR parsing algorithm
- Integer results are displayed without decimal points
