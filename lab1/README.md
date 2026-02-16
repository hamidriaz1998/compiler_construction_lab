# Compiler Construction Lab 1

This lab tokenizes simple arithmetic/assignment expressions and can evaluate them. It uses plain Python—no external dependencies.

## Prerequisites

- Python 3.10+ installed. If missing, install from https://www.python.org/downloads/ or your package manager (e.g., `sudo apt install python3 python3-venv`).

## Quick start

1. (Optional) Create and activate a virtual env:
   - `python3 -m venv .venv`
   - `source .venv/bin/activate`
2. Run the tokenizer + evaluator demo:
   - `python3 main.py`
   - It reads expressions from `inputs.txt`, prints their tokens, then evaluates them (assignments persist across inputs).

## Files

- `task1.py` — tokenizes expressions into `Token` objects.
- `main.py` — reads `inputs.txt`, prints expressions and their tokens.
- `task3.py` — evaluates token lists, supporting `+ - * /`, parentheses, and assignment.
- `inputs.txt` — sample expressions used by `main.py`.

## Example

```
python3 main.py
Expression: 3 + 4 * 2
Tokens: [NUMBER:3.0, PLUS:+, NUMBER:4.0, MULTIPLY:*, NUMBER:2.0]
Result: 11.0
```

## Troubleshooting

- If `python3` is not found, install Python or use `python` if that is your system command.
- If on Windows, replace `python3` with `py` in the commands above.
