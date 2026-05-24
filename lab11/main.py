"""
Operator Precedence Parser
Grammar:
    type          ->  standard_type
                  |   array [ num .. num ] of standard_type
    standard_type ->  integer
                  |   real

Key idea:
  The parser maintains a stack and reads input left-to-right.
  At each step it compares the rightmost terminal on the stack
  with the current input terminal using the precedence table:

      '<'  ->  SHIFT   (input has higher precedence, push it)
      '='  ->  SHIFT   (equal, they are in the same handle, push it)
      '>'  ->  REDUCE  (stack's handle is complete, replace with LHS)
      None ->  ERROR

After every reduce we immediately loop back -- we do NOT consume a
new input token -- because the newly placed non-terminal may itself
complete a larger handle that must be reduced straight away.
"""

# -----------------------------------------------------------------------------
#  TERMINALS
# -----------------------------------------------------------------------------
TERMINALS = {"array", "[", "num", "..", "]", "of", "integer", "real", "$"}

# -----------------------------------------------------------------------------
#  PRECEDENCE TABLE
#  Rows = top-of-stack terminal, Cols = current input terminal
# -----------------------------------------------------------------------------
#              array    [       num     ..      ]       of      integer  real    $
TABLE = {
    "array": {
        "array": None,
        "[": "=",
        "num": None,
        "..": None,
        "]": None,
        "of": None,
        "integer": None,
        "real": None,
        "$": None,
    },
    "[": {
        "array": None,
        "[": None,
        "num": "=",
        "..": None,
        "]": None,
        "of": None,
        "integer": None,
        "real": None,
        "$": None,
    },
    "num": {
        "array": None,
        "[": None,
        "num": None,
        "..": "=",
        "]": "=",
        "of": None,
        "integer": None,
        "real": None,
        "$": None,
    },
    "..": {
        "array": None,
        "[": None,
        "num": "=",
        "..": None,
        "]": None,
        "of": None,
        "integer": None,
        "real": None,
        "$": None,
    },
    "]": {
        "array": None,
        "[": None,
        "num": None,
        "..": None,
        "]": None,
        "of": "=",
        "integer": None,
        "real": None,
        "$": None,
    },
    "of": {
        "array": None,
        "[": None,
        "num": None,
        "..": None,
        "]": None,
        "of": None,
        "integer": "<",
        "real": "<",
        "$": None,
    },
    "integer": {
        "array": None,
        "[": None,
        "num": None,
        "..": None,
        "]": None,
        "of": None,
        "integer": None,
        "real": None,
        "$": ">",
    },
    "real": {
        "array": None,
        "[": None,
        "num": None,
        "..": None,
        "]": None,
        "of": None,
        "integer": None,
        "real": None,
        "$": ">",
    },
    "$": {
        "array": "<",
        "[": None,
        "num": None,
        "..": None,
        "]": None,
        "of": None,
        "integer": "<",
        "real": "<",
        "$": None,
    },
}

# -----------------------------------------------------------------------------
#  PRODUCTIONS  (handle -> LHS)
# -----------------------------------------------------------------------------
PRODUCTIONS = {
    ("integer",): ("standard_type", "standard_type -> integer"),
    ("real",): ("standard_type", "standard_type -> real"),
    ("standard_type",): ("type", "type -> standard_type"),
    ("array", "[", "num", "..", "num", "]", "of", "standard_type"): (
        "type",
        "type -> array [ num .. num ] of standard_type",
    ),
}

# -----------------------------------------------------------------------------
#  HELPERS
# -----------------------------------------------------------------------------


def rightmost_terminal(stack):
    for sym in reversed(stack):
        if sym in TERMINALS:
            return sym
    return "$"


def find_handle_start(stack):
    """
    Walk left through adjacent terminal pairs until we find a '<' relation.
    The handle starts just after that '<' boundary.
    """
    term_positions = [
        (i, stack[i]) for i in range(len(stack) - 1, -1, -1) if stack[i] in TERMINALS
    ]
    for k in range(len(term_positions) - 1):
        right_pos, right_sym = term_positions[k]
        left_pos, left_sym = term_positions[k + 1]
        if TABLE.get(left_sym, {}).get(right_sym) == "<":
            return left_pos + 1
    # No '<' found -- everything after the bottom '$' is the handle
    for i, sym in enumerate(stack):
        if sym == "$":
            return i + 1
    return 1


def try_reduce(stack):
    """
    Attempt to reduce the current handle on the stack.
    Returns (new_stack, rule_name) if successful, or raises ValueError.
    """
    start = find_handle_start(stack)
    handle = tuple(stack[start:])
    if handle not in PRODUCTIONS:
        raise ValueError(f"No production for handle {list(handle)}")
    lhs, rule = PRODUCTIONS[handle]
    return stack[:start] + [lhs], rule


# -----------------------------------------------------------------------------
#  TOKENIZER
# -----------------------------------------------------------------------------


def tokenize(source):
    spaced = source.replace("[", " [ ").replace("]", " ] ")
    tokens = []
    for word in spaced.split():
        tokens.append("num" if word.lstrip("-").isdigit() else word)
    tokens.append("$")
    return tokens


# -----------------------------------------------------------------------------
#  PARSER
# -----------------------------------------------------------------------------


def parse(tokens, verbose=True):
    stack = ["$"]
    idx = 0  # position in tokens[]

    def log(action, detail=""):
        if verbose:
            s = " ".join(stack)
            t = " ".join(tokens[idx:])
            print(f"  {s:<54}  {t:<33} {action} {detail}")

    if verbose:
        w = 98
        print("\n" + "=" * w)
        print(f"  Input: {' '.join(tokens)}")
        print("=" * w)
        print(f"  {'Stack':<54}  {'Remaining input':<33} Action")
        print("-" * w)

    while True:
        a = tokens[idx]
        top_term = rightmost_terminal(stack)

        # ── ACCEPT ────────────────────────────────────────────────────────────
        if top_term == "$" and a == "$":
            top = stack[-1] if len(stack) > 1 else None
            if top == "type":
                log("ACCEPT")
                if verbose:
                    print("=" * 98)
                    print("  Input accepted -- valid type.\n")
                return True
            # If standard_type is sitting at top and we're at end, reduce it
            if top == "standard_type":
                stack[-1] = "type"
                log("REDUCE ", "type -> standard_type")
                continue
            log("ERROR", "-- bad end state")
            if verbose:
                print("  Syntax error.\n")
            return False

        # ── LOOK UP RELATION ──────────────────────────────────────────────────
        rel = TABLE.get(top_term, {}).get(a)

        # ── SHIFT ('<' or '=') ────────────────────────────────────────────────
        if rel in ("<", "="):
            label = "SHIFT  " if rel == "<" else "SHIFT= "
            log(label, f'push "{a}"')
            stack.append(a)
            idx += 1

        # ── REDUCE ('>') ──────────────────────────────────────────────────────
        elif rel == ">":
            try:
                stack, rule = try_reduce(stack)
                log("REDUCE ", rule)
                # Do NOT advance idx -- check the new stack against same input
            except ValueError as e:
                log("ERROR", f"-- {e}")
                if verbose:
                    print(f"  Syntax error.\n")
                return False

        # ── NO RELATION (None) ────────────────────────────────────────────────
        else:
            if stack[-1] not in TERMINALS:
                try:
                    stack, rule = try_reduce(stack)
                    log("REDUCE ", rule)
                    continue
                except ValueError:
                    pass

            log("ERROR", f"-- no relation ({top_term!r}, {a!r})")
            if verbose:
                print(f"  Syntax error near '{a}'.\n")
            return False


# -----------------------------------------------------------------------------
#  FILE I/O
# -----------------------------------------------------------------------------


def parse_source(source, verbose=True):
    """Tokenize and parse a single source string."""
    return parse(tokenize(source), verbose=verbose)


def load_tests(path):
    """Load test cases from a file.

    Format per line:
        source string => True|False
    or just:
        source string             (assumes expected = True)

    Lines starting with '#' and blank lines are ignored.
    """
    tests = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=>" in line:
                src, expected = line.rsplit("=>", 1)
                tests.append((src.strip(), expected.strip() == "True"))
            else:
                tests.append((line, True))
    return tests


def run_tests(tests, verbose=True):
    """Run a list of (source, expected) test cases and print results."""
    passed = failed = 0
    for src, expected in tests:
        result = parse_source(src, verbose=verbose)
        ok = result == expected
        passed += ok
        failed += not ok
        print(
            f"  [{'PASS' if ok else 'FAIL'}]  '{src}'  expected={expected}  got={result}\n"
        )
    print("-" * 55)
    print(f"  {passed} passed,  {failed} failed  ({len(tests)} total)")
    print("-" * 55)
    return failed == 0


# -----------------------------------------------------------------------------
#  MAIN
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Operator precedence parser for type grammar."
    )
    parser.add_argument("source_file", nargs="?", help="Parse a single source file")
    parser.add_argument("--test-file", "-t", help="Run test cases from a file")
    parser.add_argument(
        "--quiet", "-q", action="store_true", help="Suppress verbose output"
    )
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
            ("integer", True),
            ("real", True),
            ("array [ 1 .. 10 ] of integer", True),
            ("array [ 5 .. 20 ] of real", True),
            ("array [ 1 .. 10 ] of array", False),
            ("integer real", False),
            ("array integer", False),
            ("[ integer ]", False),
            ("array [ 1 .. 10 ] of", False),
        ]
        run_tests(tests)
