# Lab 11 — Operator Precedence Parser — Complete Explanation

This directory implements an **operator-precedence parser** (a type of bottom-up shift-reduce parser) for a small subset of Pascal type declarations. The parser reads a type expression and determines whether it is syntactically valid according to the grammar.

---

## 1. Grammar

The parser handles exactly four production rules:

```
type          -> standard_type
              | array [ num .. num ] of standard_type
standard_type -> integer
              | real
```

**Terminals** (tokens): `array`, `[`, `num`, `..`, `]`, `of`, `integer`, `real`, `$` (end-of-input marker)

**Non-terminals**: `type`, `standard_type`

---

## 2. File Structure

| File | Purpose |
|------|---------|
| `main.py` | Full parser implementation + CLI |
| `README.md` | Usage instructions |
| `sample.txt` | Example input file |
| `tests/valid.txt` | Valid type expressions |
| `tests/invalid.txt` | Invalid type expressions |
| `tests/mixed.txt` | Mixed valid/invalid cases |

---

## 3. Core Concepts

### 3.1 Operator-Precedence Parsing

This is a **bottom-up** parsing technique that uses a **precedence relation table** to decide when to shift (push a token onto the stack) and when to reduce (replace a handle on the stack with a non-terminal).

There are three precedence relations between terminal symbols:

| Relation | Meaning | Action |
|----------|---------|--------|
| `'<'` | Input has higher precedence | **Shift** — push input onto stack |
| `'='` | Equal precedence (same handle) | **Shift** — push input onto stack |
| `'>'` | Handle is complete | **Reduce** — replace handle with LHS non-terminal |
| `None` | Undefined relation | **Error** |

### 3.2 The Stack and Input

The parser maintains:
- A **stack** initialized to `['$']` (bottom marker)
- An **input pointer** into the tokenized input (also terminated with `$`)

At each step, it compares the **rightmost terminal on the stack** with the **current input token**.

---

## 4. Code Breakdown

### 4.1 Terminals and Precedence Table

```python
TERMINALS = {'array', '[', 'num', '..', ']', 'of', 'integer', 'real', '$'}

TABLE = {
    'array':  {'array':None, '[':'=',  'num':None,'..':None,']':None,'of':None,'integer':None,'real':None,'$':None},
    '[':      {'array':None, '[':None, 'num':'=', '..':None,']':None,'of':None,'integer':None,'real':None,'$':None},
    'num':    {'array':None, '[':None, 'num':None,'..':'=', ']':'=', 'of':None,'integer':None,'real':None,'$':None},
    '..':     {'array':None, '[':None, 'num':'=', '..':None,']':None,'of':None,'integer':None,'real':None,'$':None},
    ']':      {'array':None, '[':None, 'num':None,'..':None,']':None,'of':'=', 'integer':None,'real':None,'$':None},
    'of':     {'array':None, '[':None, 'num':None,'..':None,']':None,'of':None,'integer':'<', 'real':'<', '$':None},
    'integer':{'array':None, '[':None, 'num':None,'..':None,']':None,'of':None,'integer':None,'real':None,'$':'>'},
    'real':   {'array':None, '[':None, 'num':None,'..':None,']':None,'of':None,'integer':None,'real':None,'$':'>'},
    '$':      {'array':'<',  '[':None, 'num':None,'..':None,']':None,'of':None,'integer':'<', 'real':'<', '$':None},
}
```

Rows are the **rightmost terminal on the stack**. Columns are the **current input token**. Each cell gives the relation.

Key relations:

| Stack terminal | Input terminal | Relation | Why |
|----------------|----------------|----------|-----|
| `$` | `integer` | `'<'` | Shift — input starts a type |
| `$` | `array` | `'<'` | Shift — input starts an array type |
| `num` | `..` | `'='` | Same handle (`num .. num`) |
| `num` | `]` | `'='` | Same handle (`num .. num ]`) |
| `]` | `of` | `'='` | Same handle (`] of`) |
| `of` | `integer` | `'<'` | Shift — `standard_type` starts after `of` |
| `integer` | `$` | `'>'` | Reduce — handle complete at end |
| `real` | `$` | `'>'` | Reduce — handle complete at end |

### 4.2 Productions

```python
PRODUCTIONS = {
    ('integer',):
        ('standard_type', 'standard_type -> integer'),
    ('real',):
        ('standard_type', 'standard_type -> real'),
    ('standard_type',):
        ('type',          'type -> standard_type'),
    ('array','[','num','..','num',']','of','standard_type'):
        ('type',          'type -> array [ num .. num ] of standard_type'),
}
```

Keys are **handles** (tuples of symbols on the stack that form a complete RHS). Values are `(LHS, description_string)`.

### 4.3 Finding the Rightmost Terminal

```python
def rightmost_terminal(stack):
    for sym in reversed(stack):
        if sym in TERMINALS:
            return sym
    return '$'
```

Scans the stack from top to bottom for the first terminal symbol. This is the symbol used to look up the precedence relation.

### 4.4 Finding Where a Handle Starts

```python
def find_handle_start(stack):
    term_positions = [
        (i, stack[i])
        for i in range(len(stack) - 1, -1, -1)
        if stack[i] in TERMINALS
    ]
    for k in range(len(term_positions) - 1):
        right_pos, right_sym = term_positions[k]
        left_pos,  left_sym  = term_positions[k + 1]
        if TABLE.get(left_sym, {}).get(right_sym) == '<':
            return left_pos + 1
    for i, sym in enumerate(stack):
        if sym == '$':
            return i + 1
    return 1
```

In operator-precedence parsing, a handle is delimited by a `'<'` on the left and a `'>'` on the right. This function walks adjacent terminal pairs from right to left, looking for a `'<'` boundary. The handle starts just after that boundary.

Example: For stack `$ array [ num .. num ] of integer`, the terminals are `$`, `array`, `[`, `num`, `..`, `num`, `]`, `of`, `integer`. The `'<'` relation between `of` and `integer` tells us the handle starts after `of`.

### 4.5 Reducing

```python
def try_reduce(stack):
    start  = find_handle_start(stack)
    handle = tuple(stack[start:])
    if handle not in PRODUCTIONS:
        raise ValueError(f"No production for handle {list(handle)}")
    lhs, rule = PRODUCTIONS[handle]
    return stack[:start] + [lhs], rule
```

Extracts the handle (top portion of the stack from `start` to end), looks it up in `PRODUCTIONS`, and replaces it with the LHS non-terminal.

### 4.6 Tokenizer

```python
def tokenize(source):
    spaced = source.replace('[', ' [ ').replace(']', ' ] ')
    tokens = []
    for word in spaced.split():
        tokens.append('num' if word.lstrip('-').isdigit() else word)
    tokens.append('$')
    return tokens
```

A minimal lexer. It inserts spaces around brackets so they get split into separate tokens, converts any numeric literal to the `num` token, and appends `$` as the end marker.

### 4.7 The Main Parse Loop

```python
def parse(tokens, verbose=True):
    stack = ['$']
    idx   = 0

    while True:
        a        = tokens[idx]
        top_term = rightmost_terminal(stack)

        # ACCEPT
        if top_term == '$' and a == '$':
            top = stack[-1] if len(stack) > 1 else None
            if top == 'type':
                return True
            if top == 'standard_type':
                stack[-1] = 'type'
                continue
            return False

        rel = TABLE.get(top_term, {}).get(a)

        # SHIFT
        if rel in ('<', '='):
            stack.append(a)
            idx += 1

        # REDUCE
        elif rel == '>':
            try:
                stack, rule = try_reduce(stack)
                # Do NOT advance idx
            except ValueError:
                return False

        # ERROR
        else:
            if stack[-1] not in TERMINALS:
                try:
                    stack, rule = try_reduce(stack)
                    continue
                except ValueError:
                    pass
            return False
```

The loop has four branches:

1. **ACCEPT**: Both stack and input are at `$`. If stack has `type`, the input is valid. If `standard_type` is on top, reduce it to `type` first. Otherwise, error.

2. **SHIFT** (`'<'` or `'='`): Push the input token onto the stack and advance the input pointer.

3. **REDUCE** (`'>'`): Call `try_reduce` to replace the handle. The input pointer is **not** advanced — after the reduce, the new non-terminal might combine with the rest of the stack to form a larger handle that must also be reduced immediately.

4. **ERROR** (no relation): First, if the top of the stack is a non-terminal, try reducing it (this handles cases where a non-terminal sits at the top without a `'>'` relation). If that fails, it's a genuine syntax error.

The **reduce-immediately** behavior (not advancing input after reduce) is the key difference from a typical LR parser. In operator-precedence parsing, a single input token can trigger a cascade of reductions.

### 4.8 Example Trace

Input: `array [ 1 .. 10 ] of integer`

Parsing steps:

```
Stack                                                       Remaining input              Action
$                                                      array [ num .. num ] of integer $  SHIFT   push "array"
$ array                                                 [ num .. num ] of integer $      SHIFT   push "["
$ array [                                                num .. num ] of integer $       SHIFT=  push "num"
$ array [ num                                             .. num ] of integer $          SHIFT=  push ".."
$ array [ num ..                                           num ] of integer $            SHIFT=  push "num"
$ array [ num .. num                                        ] of integer $               SHIFT=  push "]"
$ array [ num .. num ]                                      of integer $                 SHIFT=  push "of"
$ array [ num .. num ] of                                   integer $                    SHIFT   push "integer"
$ array [ num .. num ] of integer                           $                            REDUCE  standard_type -> integer
$ array [ num .. num ] of standard_type                     $                            REDUCE  type -> array [ num .. num ] of standard_type
$ type                                                      $                            ACCEPT
```

### 4.9 Test Loading and Running

```python
def load_tests(path):
    tests = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=>' in line:
                src, expected = line.rsplit('=>', 1)
                tests.append((src.strip(), expected.strip() == 'True'))
            else:
                tests.append((line, True))
    return tests

def run_tests(tests, verbose=True):
    passed = failed = 0
    for src, expected in tests:
        result = parse_source(src, verbose=verbose)
        ok = (result == expected)
        passed += ok; failed += not ok
        print(f"  [{'PASS' if ok else 'FAIL'}]  '{src}'  expected={expected}  got={result}\n")
    print(f"  {passed} passed,  {failed} failed  ({len(tests)} total)")
    return failed == 0
```

Test file format:
- `integer => True` / `array [ 1 .. 10 ] of array => False` — explicit expectation
- `array [ 0 .. 50 ] of integer` — defaults to `True`
- Lines starting with `#` are comments; blank lines are skipped.

### 4.10 CLI Interface

```python
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Operator precedence parser for type grammar.')
    parser.add_argument('source_file', nargs='?', help='Parse a single source file')
    parser.add_argument('--test-file', '-t', help='Run test cases from a file')
    parser.add_argument('--quiet', '-q', action='store_true', help='Suppress verbose output')
    args = parser.parse_args()

    if args.source_file:
        with open(args.source_file) as f:
            src = f.read().strip()
        parse_source(src, verbose=not args.quiet)

    elif args.test_file:
        tests = load_tests(args.test_file)
        run_tests(tests, verbose=not args.quiet)

    else:
        tests = [
            ("integer",                      True),
            ("real",                         True),
            ("array [ 1 .. 10 ] of integer", True),
            ("array [ 5 .. 20 ] of real",    True),
            ("array [ 1 .. 10 ] of array",   False),
            ("integer real",                 False),
            ("array integer",                False),
            ("[ integer ]",                  False),
            ("array [ 1 .. 10 ] of",         False),
        ]
        run_tests(tests)
```

Three modes:
1. `python main.py <file>` — parse a single source file with verbose tracing
2. `python main.py --test-file <file>` — run external test cases (from `tests/` directory)
3. `python main.py` (no arguments) — run the inline test battery

Add `--quiet` to suppress the verbose parse trace.

---

## 5. The Test Suite

### `tests/valid.txt` — All expect `True`

```
integer
real
array [ 1 .. 10 ] of integer
array [ 5 .. 20 ] of real
array [ 0 .. 100 ] of real
array [ 1 .. 5 ] of integer
```

### `tests/invalid.txt` — All expect `False`

```
array [ 1 .. 10 ] of array => False
integer real           => False
array integer          => False
[ integer ]            => False
array [ 1 .. 10 ] of   => False
array of integer       => False
integer array          => False
```

### `tests/mixed.txt` — Mixed expectations

Contains the same cases as above with explicit `=> True` / `=> False` annotations.

---

## 6. Running the Code

```bash
# Inline tests
python main.py

# Single file
python main.py sample.txt

# External test file
python main.py --test-file tests/mixed.txt

# Suppress trace
python main.py sample.txt --quiet
```

---

## 7. Summary of the Algorithm

1. **Tokenize** the input string into a list of terminals, ending with `$`.
2. **Initialize** stack to `['$']` and input pointer to `0`.
3. **Loop**:
   - Get the rightmost terminal on the stack and the current input token.
   - If both are `$` and stack has `type` → **accept**.
   - Look up the precedence relation `TABLE[stack_term][input_term]`.
   - **`'<'` or `'='`** → shift the input token onto the stack, advance input.
   - **`'>'`** → find the handle (between the last `'<'` and the top), reduce it to a non-terminal using `PRODUCTIONS`. Do NOT advance input.
   - **`None`** → try reducing a non-terminal at stack top; if that fails, report error.
4. The **handle boundary** is found by scanning terminal pairs right-to-left for a `'<'` relation.
5. After every reduce, the parser immediately re-checks the new stack against the **same** input token, allowing cascading reductions.
