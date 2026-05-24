# Pascal Subset LL(1) Table-Driven Parser

A table-driven LL(1) predictive parser for a subset of Pascal, built from the transformed CFG in `subset_pascal_cfg_transformed.md`.

## Components

- **`lexer.py`** — Tokenizer for the Pascal subset (copied from lab9)
- **`ll1_parser.py`** — LL(1) parser with FIRST/FOLLOW set computation and table-driven parsing

## Grammar

Based on `subset_pascal_cfg_transformed.md` — the original LALR(1) grammar transformed to be LL(1)-compatible via:

1. **Left recursion elimination**: `A → A α | β` → `A → β A'`, `A' → α A' | ε`
2. **Left factoring**: `A → α β₁ | α β₂` → `A → α A'`, `A' → β₁ | β₂`

### Full Transformed Grammar

```
program                  →  program id ( identifier_list ) ;
                            declarations subprogram_declarations compound_statement

identifier_list          →  id identifier_list'
identifier_list'         →  , id identifier_list' | ε

declarations             →  declarations'
declarations'            →  var identifier_list : type ; declarations' | ε

type                     →  standard_type
                          |  array [ num .. num ] of standard_type

standard_type            →  integer | real

subprogram_declarations  →  subprogram_declarations'
subprogram_declarations' →  subprogram_declaration ; subprogram_declarations' | ε

subprogram_declaration   →  subprogram_head declarations compound_statement

subprogram_head          →  function  id arguments : standard_type ;
                          |  procedure id arguments ;

arguments                →  ( parameter_list ) | ε

parameter_list           →  identifier_list : type parameter_list'
parameter_list'          →  ; identifier_list : type parameter_list' | ε

compound_statement       →  begin optional_statements end

optional_statements      →  statement_list | ε

statement_list           →  statement statement_list'
statement_list'          →  ; statement statement_list' | ε

statement                →  id statement_tail
                          |  compound_statement
                          |  if expression then statement else statement
                          |  while expression do statement

statement_tail           →  assignop expression
                          |  [ expression ] assignop expression
                          |  ( expression_list )
                          |  ε

expression_list          →  expression expression_list'
expression_list'         →  , expression expression_list' | ε

expression               →  simple_expression expression'
expression'              →  relop simple_expression | ε

simple_expression        →  term simple_expression'
                          |  sign term simple_expression'
simple_expression'       →  addop term simple_expression' | ε

term                     →  factor term'
term'                    →  mulop factor term' | ε

factor                   →  id factor'
                          |  num
                          |  ( expression )
                          |  not factor
factor'                  →  ( expression_list ) | ε

sign                     →  + | -
```

## How the LL(1) Parser Works

### FIRST Sets

`FIRST(α)` = terminals that can begin any string derived from α.

Computed iteratively:

- If X is a terminal: `FIRST(X) = {X}`
- If X → ε: add ε to `FIRST(X)`
- If X → Y₁Y₂...Yₖ: add `FIRST(Y₁) - {ε}` to `FIRST(X)`; if Y₁ can derive ε, also add `FIRST(Y₂)`, etc.

### FOLLOW Sets

`FOLLOW(A)` = terminals that can appear immediately after A in some sentential form.

- Place `$` in `FOLLOW(start)`
- If `A → αBβ`: add `FIRST(β) - {ε}` to `FOLLOW(B)`
- If `A → αB` or `β ⇒* ε`: add `FOLLOW(A)` to `FOLLOW(B)`

### Parsing Table

`M[NonTerminal, Terminal] → Production`

For each production `A → α`:

- For each `a ∈ FIRST(α)`: `M[A, a] = A → α`
- If `ε ∈ FIRST(α)`: for each `b ∈ FOLLOW(A)`: `M[A, b] = A → α`

If any cell gets two entries, the grammar is **not LL(1)** — the parser reports conflicts.

### Table-Driven Parsing

Uses an explicit stack instead of recursion:

```
Stack: [$, start_symbol]     Input: tokens + $

while not done:
    X = stack top, a = current token
    if X == a == $:          ACCEPT
    if X is terminal:
        if X == a:           pop, advance input
        else:                ERROR
    if X is non-terminal:
        look up M[X, a]
        if production X → Y₁Y₂...Yₖ:
            pop X, push Yₖ...Y₂Y₁  (reverse order)
        else:                ERROR
```

## Usage

### Run the LL(1) parser (shows FIRST, FOLLOW, table, and parses)

```bash
# Pass a .pas source file
python3 ll1_parser.py samples/factorial.pas

# Other samples
python3 ll1_parser.py samples/gcd.pas
python3 ll1_parser.py samples/max.pas
python3 ll1_parser.py samples/power.pas
```

### Tokenize only (without parsing)

```bash
python3 lexer.py source.pas
```

### Use programmatically

```python
from ll1_parser import compute_first, compute_follow, build_parsing_table, LL1Parser

first = compute_first()
follow = compute_follow(first)
table = build_parsing_table(first, follow)

parser = LL1Parser(tokens, table, first, follow)
productions = parser.parse()  # raises SyntaxError on failure
```

## Sample Programs

- `factorial.pas` — recursive factorial function
- `power.pas` — recursive power function
- `max.pas` — maximum of two numbers
- `gcd.pas` — GCD of two numbers

All four samples parse successfully with zero table conflicts.

## Output

Running `python3 ll1_parser.py tokens.txt` prints:

1. **FIRST sets** for all 33 non-terminals
2. **FOLLOW sets** for all 33 non-terminals
3. **LL(1) parsing table** (non-empty entries only)
4. **Parse result** — either "Parsing successful!" with the full leftmost derivation, or a syntax error with details
