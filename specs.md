# Calculator Implementation Specification

## Overview
This calculator is implemented in Python using the Lark parser generator. It parses mathematical expressions according to a context-free grammar and evaluates them recursively through an Abstract Syntax Tree (AST).

## Files

### 1. grammar.lark
Contains the Lark grammar specification that defines the syntax of valid mathematical expressions.

### 2. calculator_cfg.py
Contains the Python implementation including the parser, AST transformer, and evaluator.

### 3. specs.md
This file - contains detailed specifications of the implementation.

---

## Grammar Design

### Original Ambiguous Grammar
The assignment started with this ambiguous grammar:
```
exp -> exp '+' exp
exp -> exp '*' exp
exp -> exp '^' exp
exp -> exp '-' exp
exp -> '-' exp 
exp -> 'log' exp 'base' exp
exp -> '(' exp ')'
exp -> number
```

### Disambiguated Grammar
The grammar was restructured to eliminate ambiguity and enforce proper operator precedence and associativity:

```lark
?start: sum

?sum: product
    | sum "+" product   -> add
    | sum "-" product   -> sub

?product: unary
    | product "*" unary -> mul

?unary: power
    | "-" unary         -> neg

?power: log
    | log "^" power     -> exp

?log: atom
    | "log" log "base" atom -> logarithm

?atom: NUMBER           -> number
     | "(" sum ")"

%import common.NUMBER
%import common.WS
%ignore WS
```

### Key Grammar Features

**Precedence Hierarchy** (from lowest to highest):
1. **Addition/Subtraction** (`+`, `-`) - lowest precedence
2. **Multiplication** (`*`)
3. **Unary Negation** (`-`)
4. **Exponentiation** (`^`)
5. **Logarithm** (`log base`)
6. **Parentheses and Numbers** - highest precedence

**Associativity**:
- **Left-associative**: `+`, `-`, `*` 
  - Example: `1+2+3` parses as `(1+2)+3`
- **Right-associative**: `^`
  - Example: `2^3^2` parses as `2^(3^2)` = 512
- **Unary operators**: Apply from right to left
  - Example: `--1` parses as `-(-1)` = 1

**Special Precedence Note**:
- Unary minus has **lower precedence than exponentiation**
- This means `-3^2` parses as `-(3^2)` = -9, not `(-3)^2` = 9
- This matches standard mathematical convention

---

## Code Structure

### Main Components

#### 1. Grammar Loading
```python
with open('grammar.lark', 'r') as f:
    grammar = f.read()
parser = Lark(grammar, parser='lalr')
```
- Reads the grammar from `grammar.lark`
- Creates a Lark parser instance using the LALR parsing algorithm
- LALR is efficient and suitable for our grammar

#### 2. CalculateTree Transformer Class
This class inherits from `lark.Transformer` and implements the visitor pattern to transform the parse tree into computed values.

**Methods**:

- **`number(self, n)`**
  - **Purpose**: Convert number tokens from the parse tree to Python float values
  - **Input**: Token representing a number
  - **Output**: Float value
  - **Logic**: Direct conversion using `float(n)`

- **`add(self, left, right)`**
  - **Purpose**: Perform addition
  - **Input**: Two numeric values (left and right operands)
  - **Output**: Sum of left and right
  - **Logic**: `left + right`

- **`sub(self, left, right)`**
  - **Purpose**: Perform subtraction
  - **Input**: Two numeric values (left and right operands)
  - **Output**: Difference of left and right
  - **Logic**: `left - right`

- **`mul(self, left, right)`**
  - **Purpose**: Perform multiplication
  - **Input**: Two numeric values (left and right operands)
  - **Output**: Product of left and right
  - **Logic**: `left * right`

- **`exp(self, base, exponent)`**
  - **Purpose**: Perform exponentiation
  - **Input**: Base and exponent values
  - **Output**: Base raised to the power of exponent
  - **Logic**: `base ** exponent`
  - **Note**: Right-associativity is handled by the grammar structure

- **`neg(self, value)`**
  - **Purpose**: Perform unary negation
  - **Input**: A numeric value
  - **Output**: Negative of the input value
  - **Logic**: `-value`

- **`logarithm(self, value, base)`**
  - **Purpose**: Compute logarithm with specified base
  - **Input**: Value and base
  - **Output**: log_base(value)
  - **Logic**: Uses Python's `math.log(value, base)`

**Decorator**: `@v_args(inline=True)`
- This decorator automatically unpacks the arguments from the parse tree nodes
- Instead of receiving a list of children, each method receives individual arguments
- Makes the code cleaner and more readable

#### 3. calculate() Function
**Purpose**: Main evaluation function that orchestrates parsing and transformation

**Input**: String expression (e.g., "1+2*3")

**Output**: Numeric result of the expression

**Internal Logic**:
1. Call `parser.parse(expression)` to generate parse tree from input string
2. Create an instance of `CalculateTree` transformer
3. Call `transform(tree)` to recursively traverse and evaluate the parse tree
4. Return the final computed result

**Flow**:
```
Input String → Parser → Parse Tree → Transformer → Result
```

#### 4. main() Function
**Purpose**: Handle command-line interface

**Input**: Command-line arguments (expects expression as argv[1])

**Output**: Prints the result to stdout

**Internal Logic**:
1. Validate that exactly one argument is provided
2. Extract the expression from command-line arguments
3. Call `calculate()` to evaluate the expression
4. Format output: integers are printed without decimal point, floats with decimal
5. Handle errors gracefully and exit with appropriate status code

**Error Handling**:
- Incorrect number of arguments → Usage message and exit
- Parse or evaluation errors → Error message to stderr and exit with code 1

---

## Program Flow

### Execution Sequence
1. **Initialization**
   - Load grammar from `grammar.lark`
   - Create Lark parser with LALR algorithm

2. **Input Processing**
   - Receive expression string from command line
   - Validate input format

3. **Parsing Phase**
   - Tokenize input string
   - Apply grammar rules to construct parse tree
   - Parse tree represents the syntactic structure of the expression

4. **Transformation Phase**
   - Traverse parse tree depth-first (post-order)
   - At each node, apply corresponding transformer method
   - Child nodes are evaluated before parent nodes
   - Operators combine child values according to their semantics

5. **Output**
   - Format final result
   - Print to stdout

### Example Execution Flow
For input `"2^3+1"`:

1. **Parse**: Creates tree structure:
   ```
   add
   ├── exp
   │   ├── number(2)
   │   └── number(3)
   └── number(1)
   ```

2. **Transform** (bottom-up):
   - `number(2)` → 2.0
   - `number(3)` → 3.0
   - `exp(2.0, 3.0)` → 8.0
   - `number(1)` → 1.0
   - `add(8.0, 1.0)` → 9.0

3. **Output**: `9`

---

## Order of Operations

### Implementation Strategy
Order of operations is enforced through **grammar structure**, not through post-processing or evaluation logic.

**Key Principle**: 
- Lower precedence operators are defined at higher levels of the grammar hierarchy
- Higher precedence operators are defined at lower levels (closer to atoms)
- The grammar nesting determines evaluation order

### Precedence Rules Implemented

1. **Parentheses**: Highest priority - override all other rules
2. **Logarithm**: Evaluated before exponentiation
3. **Exponentiation**: Right-associative, evaluated before unary minus
4. **Unary Negation**: Evaluated after exponentiation, before multiplication
5. **Multiplication**: Evaluated before addition/subtraction
6. **Addition/Subtraction**: Lowest priority, left-associative

### Example Demonstrations

**Example 1**: `1+2*3 = 7`
- Multiplication binds tighter than addition
- Evaluates as `1+(2*3)` not `(1+2)*3`

**Example 2**: `2^3^2 = 512`
- Exponentiation is right-associative
- Evaluates as `2^(3^2) = 2^9 = 512`
- Not `(2^3)^2 = 8^2 = 64`

**Example 3**: `-3^2 = -9`
- Unary minus has lower precedence than exponentiation
- Evaluates as `-(3^2) = -9`
- Not `(-3)^2 = 9`

**Example 4**: `log 8 base 2 + 1 = 4`
- Logarithm has higher precedence than addition
- Evaluates as `(log 8 base 2) + 1 = 3 + 1 = 4`

---

## Testing

### Test Cases Verified

| Expression | Expected | Actual | Status |
|------------|----------|--------|--------|
| `1+2*3` | 7 | 7 | ✓ |
| `2-(4+2)` | -4 | -4 | ✓ |
| `(3+2)*2` | 10 | 10 | ✓ |
| `--1` | 1 | 1 | ✓ |
| `2^3^2` | 512 | 512 | ✓ |
| `2^3+1` | 9 | 9 | ✓ |
| `2^3*2` | 16 | 16 | ✓ |
| `log 8 base 2` | 3 | 3 | ✓ |
| `log 8 base 2 + 1` | 4 | 4 | ✓ |
| `-3^2` | -9 | -9 | ✓ |

All test cases pass successfully.

---

## Design Decisions

### 1. Grammar-Based Precedence
**Decision**: Encode operator precedence directly in grammar structure rather than in evaluation logic.

**Rationale**: 
- More maintainable and declarative
- Easier to reason about and modify
- Standard approach in compiler design
- Parser generator handles complexity automatically

### 2. LALR Parser
**Decision**: Use LALR parsing algorithm.

**Rationale**:
- Efficient for our grammar
- Handles left recursion well
- Industry standard for this type of parsing

### 3. Single-Pass Evaluation
**Decision**: Evaluate expression during AST transformation, not in a separate pass.

**Rationale**:
- Simpler code structure
- More efficient (no intermediate AST storage needed)
- Sufficient for calculator application

### 4. Direct Value Computation
**Decision**: Transform methods return computed values rather than AST nodes.

**Rationale**:
- Calculator doesn't need to preserve AST structure
- More straightforward implementation
- Better performance

### 5. Integer Output Formatting
**Decision**: Print integers without decimal point, floats with decimal.

**Rationale**:
- Cleaner output for integer results
- Matches expected test output format
- Still preserves precision for non-integer results

---

## Limitations and Assumptions

### Assumptions
1. Input expressions follow the defined grammar
2. Numbers are valid Python floats
3. Logarithm arguments are positive
4. No division by zero in exponentiation

### Limitations
1. No error recovery - invalid syntax causes program termination
2. Limited to operations defined in grammar (+, -, *, ^, log, unary -)
3. No support for variables or functions beyond `log`
4. No support for implicit multiplication (e.g., `2(3)`)

---

## Dependencies

- **Python 3.x**: Programming language
- **lark-parser**: Parser generator library
- **math**: Standard library for logarithm function
- **sys**: Standard library for command-line interface

---

## Usage

```bash
python calculator_cfg.py "expression"
```

**Examples**:
```bash
python calculator_cfg.py "1+2*3"          # Output: 7
python calculator_cfg.py "2^3^2"          # Output: 512
python calculator_cfg.py "log 8 base 2"   # Output: 3
```

---

## Conclusion

This implementation successfully creates a calculator that:
- Parses mathematical expressions according to a well-defined grammar
- Enforces correct operator precedence and associativity
- Evaluates expressions recursively through AST transformation
- Handles all required test cases correctly
- Provides clean, maintainable code structure

The use of Lark parser generator allows for a declarative specification of the grammar while automatically handling the complex parsing logic.
