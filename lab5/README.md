# Lab 3 — Lexer Implementations (State, Stateless, Table)

This repository contains three lexer implementations for a small Pascal-like language and a simple buffer manager used by the lexers. This README explains how to run the code, the file layout, and how to add / run more tests

---

## Quick overview

- There are three lexer approaches:
  - `state` — classic state-machine implementation (`lexers/state_approach.py`)
  - `stateless` — stateless scanning functions (`lexers/stateless_approach.py`)
  - `table` — transition-table-driven scanner (`lexers/table_approach.py`)
- A `BufferManager` supports double-buffered reading with a reader/producer model (`buffer_manager.py`).
- `driver.py` is the runner that wires a `BufferManager` to a chosen lexer and prints tokens.

---

## Prerequisites

- Python 3.8+ (the code uses `match` in some places; if your Python is older, use the `state` variant source adapted for `if`/`elif`).
- Optional: `rich` package if you want pretty tables:
  - `pip install rich`

---

## Running the lexers

Run `driver.py`:

```bash
cd lab3
python3 driver.py --lexer state  test.pas
python3 driver.py --lexer stateless test.pas
python3 driver.py --lexer table   test.pas

# With pretty output (requires `rich`)
python3 driver.py --rich --lexer table test.pas
```

Notes:
- The `--lexer` option accepts `state`, `stateless`, or `table`.

---

## File / directory structure

Top-level relevant files in `lab3/`:

- `driver.py` — main entry point that picks a lexer and prints tokens.
- `buffer_manager.py` — double-buffered reader with synchronization.
- `test_inputs/` — additional sample input programs.
- `lexers/` (package):
  - `__init__.py` — package marker
  - `lexer.py` — shared token definitions, helpers, base `Lexer` class
  - `state_approach.py` — stateful lexer
  - `stateless_approach.py` — stateless lexer
  - `table_approach.py` — table-based lexer

---

## How the lexers map to tokens

- Identifiers / keywords: `ID` or keyword token (`PROGRAM`, `VAR`, `BEGIN`, etc.)
- Integers: token type `INTEGER`
- Reals: token type `REAL`
- Operators: mapped via `OPERATORS` dict in `lexers/lexer.py`
- Special sequences handled: `:=`, `..`, `<=`, `>=`, `<>`

See `lexers/lexer.py` for the canonical token names and helper functions (`is_letter`, `is_digit`, `is_alnum`).

---

## Adding tests / inputs

- Drop `.pas` files into `test_inputs/`.
- Run them with `driver.py` as shown above.
- If you want to compare token streams from different lexers, you can redirect output to files and use `diff`:

```bash
cd lab3
python3 driver.py --lexer state  test_inputs/sample1.pas > state.tokens
python3 driver.py --lexer table  test_inputs/sample1.pas > table.tokens
diff -u state.tokens table.tokens
```

---
