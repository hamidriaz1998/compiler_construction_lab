#!/usr/bin/env python3
"""
compare_lexers.py

Run all three lexer implementations on every .pas file under `test_inputs/`
and report any differences in token streams.

Usage:
    python3 compare_lexers.py                 # runs on ./test_inputs directory
    python3 compare_lexers.py path/to/inputs  # runs on specified directory

The script expects to be executed from the lab5 directory (so that imports like
`from lexers.state_approach import ...` and `from buffer_manager import BufferManager`
work correctly). If you prefer to run this from a different working directory,
adjust PYTHONPATH accordingly or run via `python -m`.
"""

from __future__ import annotations

import argparse
import difflib
import os
import sys
import traceback
from typing import List, Tuple

# Local imports (expected when running from lab5/ directory)
try:
    from buffer_manager import BufferManager
    from lexers.lexer import Token
    from lexers.state_approach import StateApproachLexer
    from lexers.stateless_approach import StatelessLexer
    from lexers.table_approach import TableLexer
except Exception:
    # Provide a clear error message rather than a raw ImportError stack
    print(
        "Error: could not import project modules. Make sure you run this script from the "
        "lab5 directory (i.e. `cd lab5 && python3 compare_lexers.py`).",
        file=sys.stderr,
    )
    raise


def tokenize_with(lexer_cls, content: str) -> List[Tuple[str, str, int]]:
    """
    Create a BufferManager for the content, instantiate lexer_cls with it,
    and return a list of token tuples (type, value, line).
    """
    buf = BufferManager()
    buf.fill(1, content)
    buf.active = 1
    buf.forward = 0
    buf.done = True

    lexer = lexer_cls(buf)

    tokens: List[Tuple[str, str, int]] = []
    while True:
        tok = lexer.next_token()
        # Assume lexers return Token dataclass with fields: type, value, line
        if tok.type == "EOF":
            break
        tokens.append((tok.type, tok.value, tok.line))
    return tokens


def tokens_to_lines(tokens: List[Tuple[str, str, int]]) -> List[str]:
    """
    Represent token list as human-readable lines for diffing.
    """
    lines = []
    for ttype, tval, line in tokens:
        # make sure tab/newline characters in lexeme are visible
        safe_val = tval.replace("\n", "\\n").replace("\t", "\\t")
        lines.append(f"{line:4} | {ttype:12} | {safe_val}")
    return lines


def compare_token_lists(a: List[str], b: List[str]) -> List[str]:
    """
    Return a unified diff between two lists of token lines.
    """
    return list(difflib.unified_diff(a, b, fromfile="A", tofile="B", lineterm=""))


def find_pas_files(directory: str) -> List[str]:
    files = []
    for name in sorted(os.listdir(directory)):
        if name.lower().endswith(".pas"):
            files.append(os.path.join(directory, name))
    return files


def main():
    parser = argparse.ArgumentParser(
        description="Compare lexer outputs across implementations"
    )
    parser.add_argument(
        "inputs_dir",
        nargs="?",
        default="test_inputs",
        help="Directory containing .pas test files (default: test_inputs)",
    )
    args = parser.parse_args()

    inputs_dir = args.inputs_dir
    if not os.path.isdir(inputs_dir):
        print(f"Error: input directory '{inputs_dir}' not found.", file=sys.stderr)
        sys.exit(2)

    files = find_pas_files(inputs_dir)
    if not files:
        print(f"No .pas files found in '{inputs_dir}'.", file=sys.stderr)
        sys.exit(0)

    # Map label -> lexer class
    lexers = {
        "state": StateApproachLexer,
        "stateless": StatelessLexer,
        "table": TableLexer,
    }

    overall_diffs = 0

    for path in files:
        print("=" * 72)
        print(f"File: {path}")
        print("-" * 72)
        try:
            with open(path, "r") as fh:
                content = fh.read()
        except Exception as e:
            print(f"  Failed to read file: {e}", file=sys.stderr)
            continue

        results = {}
        errors = {}

        # Tokenize with each lexer
        for name, cls in lexers.items():
            try:
                toks = tokenize_with(cls, content)
                lines = tokens_to_lines(toks)
                results[name] = lines
                print(f"  {name}: {len(lines)} tokens")
            except Exception as exc:
                tb = traceback.format_exc()
                errors[name] = tb
                print(f"  {name}: ERROR during tokenization (see details below)")

        # Print any errors
        if errors:
            for name, tb in errors.items():
                print(f"\n--- Error from lexer '{name}' ---")
                print(tb)
            # If some lexers failed, we skip diff for that file
            print("Skipping comparisons for this file due to errors.")
            continue

        # Compare pairwise
        pairs = [("state", "stateless"), ("state", "table"), ("stateless", "table")]
        file_has_diff = False
        for a, b in pairs:
            a_lines = results.get(a, [])
            b_lines = results.get(b, [])
            if a_lines == b_lines:
                print(f"  [OK] {a} == {b} (token streams identical)")
            else:
                file_has_diff = True
                overall_diffs += 1
                print(f"  [DIFF] {a} != {b} (showing unified diff):")
                diff = compare_token_lists(a_lines, b_lines)
                # Print the diff with indentation for readability
                for line in diff:
                    print("    " + line)
                print()

        if not file_has_diff:
            print("  All lexers produced identical token streams for this file.")

    print("=" * 72)
    if overall_diffs == 0:
        print("Comparison complete: no differences found across lexers.")
        sys.exit(0)
    else:
        print(f"Comparison complete: {overall_diffs} differing file-pairs found.")
        sys.exit(1)


if __name__ == "__main__":
    main()
