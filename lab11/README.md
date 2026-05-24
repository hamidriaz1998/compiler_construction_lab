# Lab 11 — Operator Precedence Parser

An operator-precedence parser for a part of subset of pascal language

## Grammar

```
type          -> standard_type
              | array [ num .. num ] of standard_type
standard_type -> integer
              | real
```

## Usage

### Run default inline tests

```
python main.py
```

### Parse a single source file

```
echo "array [ 1 .. 10 ] of integer" > input.txt
python main.py input.txt
python main.py sample.txt
```

### Run test cases from a file

Test file format — one case per line; `=> True` / `=> False` sets the expectation (defaults to `True`):

```
integer => True
array [ 1 .. 10 ] of array => False
array [ 0 .. 50 ] of integer
```

```
python main.py --test-file tests/valid.txt
python main.py --test-file tests/invalid.txt
python main.py --test-file tests/mixed.txt
```

### Suppress verbose parse trace

```
python main.py input.txt --quiet
python main.py --test-file tests/mixed.txt --quiet
```

## Test Files

| File               | Contents                   |
|--------------------|----------------------------|
| `tests/valid.txt`   | Valid type expressions     |
| `tests/invalid.txt` | Invalid type expressions   |
| `tests/mixed.txt`   | Mixed valid / invalid      |
| `sample.txt`        | Single valid expression    |
