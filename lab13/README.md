# Lab 13 — Symbol Table Manager

Hash-based symbol table with nested scope management, integrated into a recursive descent parser for Subset Pascal.

## Requirements

- Python 3.10+
- `rich` (table output): `pip install rich`

## Files

| File              | Purpose                                                                              |
| ----------------- | ------------------------------------------------------------------------------------ |
| `symbol_table.py` | hash table (size 211), separate chaining, scope stack with `begin_scope`/`end_scope` |
| `lexer.py`        | Subset Pascal lexer with line number tracking                                        |
| `parser.py`       | Recursive descent parser with symbol table integration                               |
| `main.py`         | Driver — reads `.pas` file, prints tokens, runs parser, prints final global table    |

## Usage

```bash
python main.py tests/valid.pas
```

## Test cases

| File                     | Expected result                                            |
| ------------------------ | ---------------------------------------------------------- |
| `tests/valid.pas`        | Parses successfully — vars, arrays, functions, procedures  |
| `tests/duplicate.pas`    | `duplicate identifier 'x'`                                 |
| `tests/undeclared.pas`   | `undeclared identifier 'y'`                                |
| `tests/nested_scope.pas` | Shadowing — `x: integer` in global, `x: real` in procedure |
| `tests/func_shadow.pas`  | Parameter `x` shadows global `x`                           |
