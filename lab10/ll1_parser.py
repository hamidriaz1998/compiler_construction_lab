from __future__ import annotations

from lexer import Lexer

EPSILON = "ε"
DOLLAR = "$"

# ---------------------------------------------------------------------------
# 1. Grammar encoding
# ---------------------------------------------------------------------------

GRAMMAR: dict[str, list[list[str]]] = {
    "_start": [
        [
            "program",
            "id",
            "(",
            "identifier_list",
            ")",
            ";",
            "declarations",
            "subprogram_declarations",
            "compound_statement",
        ],
    ],
    "identifier_list": [
        ["id", "identifier_list'"],
    ],
    "identifier_list'": [
        [",", "id", "identifier_list'"],
        [EPSILON],
    ],
    "declarations": [
        ["declarations'"],
    ],
    "declarations'": [
        ["var", "identifier_list", ":", "type", ";", "declarations'"],
        [EPSILON],
    ],
    "type": [
        ["standard_type"],
        ["array", "[", "num", ".", ".", "num", "]", "of", "standard_type"],
    ],
    "standard_type": [
        ["integer"],
        ["real"],
    ],
    "subprogram_declarations": [
        ["subprogram_declarations'"],
    ],
    "subprogram_declarations'": [
        ["subprogram_declaration", ";", "subprogram_declarations'"],
        [EPSILON],
    ],
    "subprogram_declaration": [
        ["subprogram_head", "declarations", "compound_statement"],
    ],
    "subprogram_head": [
        ["function", "id", "arguments", ":", "standard_type", ";"],
        ["procedure", "id", "arguments", ";"],
    ],
    "arguments": [
        ["(", "parameter_list", ")"],
        [EPSILON],
    ],
    "parameter_list": [
        ["identifier_list", ":", "type", "parameter_list'"],
    ],
    "parameter_list'": [
        [";", "identifier_list", ":", "type", "parameter_list'"],
        [EPSILON],
    ],
    "compound_statement": [
        ["begin", "optional_statements", "end"],
    ],
    "optional_statements": [
        ["statement_list"],
        [EPSILON],
    ],
    "statement_list": [
        ["statement", "statement_list'"],
    ],
    "statement_list'": [
        [";", "statement", "statement_list'"],
        [EPSILON],
    ],
    "statement": [
        ["id", "statement_tail"],
        ["compound_statement"],
        ["if", "expression", "then", "statement", "else", "statement"],
        ["while", "expression", "do", "statement"],
    ],
    "statement_tail": [
        ["assignop", "expression"],
        ["[", "expression", "]", "assignop", "expression"],
        ["(", "expression_list", ")"],
        [EPSILON],
    ],
    "variable": [
        ["id", "variable'"],
    ],
    "variable'": [
        ["[", "expression"],
        [EPSILON],
    ],
    "procedure_statement": [
        ["id", "procedure_statement'"],
    ],
    "procedure_statement'": [
        ["(", "expression_list", ")"],
        [EPSILON],
    ],
    "expression_list": [
        ["expression", "expression_list'"],
    ],
    "expression_list'": [
        [",", "expression", "expression_list'"],
        [EPSILON],
    ],
    "expression": [
        ["simple_expression", "expression'"],
    ],
    "expression'": [
        ["relop", "simple_expression"],
        [EPSILON],
    ],
    "simple_expression": [
        ["term", "simple_expression'"],
        ["sign", "term", "simple_expression'"],
    ],
    "simple_expression'": [
        ["addop", "term", "simple_expression'"],
        [EPSILON],
    ],
    "term": [
        ["factor", "term'"],
    ],
    "term'": [
        ["mulop", "factor", "term'"],
        [EPSILON],
    ],
    "factor": [
        ["id", "factor'"],
        ["num"],
        ["(", "expression", ")"],
        ["not", "factor"],
    ],
    "factor'": [
        ["(", "expression_list", ")"],
        [EPSILON],
    ],
    "sign": [
        ["+"],
        ["-"],
    ],
}

# ---------------------------------------------------------------------------
# 2. Terminal / Non-terminal classification helpers
# ---------------------------------------------------------------------------

_ALL_NONTERMINALS = list(GRAMMAR.keys())

_ALL_TERMINALS_IN_GRAMMAR: set[str] = set()
for alts in GRAMMAR.values():
    for alt in alts:
        for sym in alt:
            if sym != EPSILON and sym not in GRAMMAR:
                _ALL_TERMINALS_IN_GRAMMAR.add(sym)

KEYWORD_LEXEMES = {
    "program",
    "var",
    "array",
    "of",
    "integer",
    "real",
    "function",
    "procedure",
    "begin",
    "end",
    "if",
    "then",
    "else",
    "while",
    "do",
    "not",
    "or",
    "div",
    "mod",
    "and",
}

# For the parsing table, grammar terminals map to the **column key** used for lookup.
# Keywords are looked up by their lexeme (not "KEYWORD" type).
TERMINAL_TO_TOKEN_TYPES: dict[str, set[str]] = {}
for t in _ALL_TERMINALS_IN_GRAMMAR:
    if t in KEYWORD_LEXEMES:
        # Each keyword is its own column in the parsing table
        TERMINAL_TO_TOKEN_TYPES[t] = {t}
    elif t in {"id", "num"}:
        TERMINAL_TO_TOKEN_TYPES[t] = {t}
    elif t in {"relop", "addop", "mulop", "assignop"}:
        TERMINAL_TO_TOKEN_TYPES[t] = {t}
    elif t in {"(", ")", "[", "]", ":", ",", ";", "."}:
        TERMINAL_TO_TOKEN_TYPES[t] = {t}
    elif t in {"+", "-"}:
        # sign distinguishes + vs - by lexeme
        TERMINAL_TO_TOKEN_TYPES[t] = {t}
    else:
        TERMINAL_TO_TOKEN_TYPES[t] = {t}

_LEXER_TOKEN_TYPES: set[str] = set()
for v in TERMINAL_TO_TOKEN_TYPES.values():
    _LEXER_TOKEN_TYPES.update(v)
_LEXER_TOKEN_TYPES.add(DOLLAR)


def is_terminal(sym: str) -> bool:
    return sym not in GRAMMAR and sym != EPSILON


def is_nonterminal(sym: str) -> bool:
    return sym in GRAMMAR


# ---------------------------------------------------------------------------
# 3. FIRST set computation
# ---------------------------------------------------------------------------


def compute_first() -> dict[str, set[str]]:
    """Return FIRST set for every non-terminal."""
    first: dict[str, set[str]] = {nt: set() for nt in GRAMMAR}

    changed = True
    while changed:
        changed = False
        for nt, alts in GRAMMAR.items():
            for alt in alts:
                for sym in alt:
                    if sym == EPSILON:
                        if EPSILON not in first[nt]:
                            first[nt].add(EPSILON)
                            changed = True
                        break
                    if is_terminal(sym):
                        if sym not in first[nt]:
                            first[nt].add(sym)
                            changed = True
                        break
                    # sym is a non-terminal
                    before = len(first[nt])
                    first[nt] |= first[sym] - {EPSILON}
                    if len(first[nt]) > before:
                        changed = True
                    if EPSILON not in first[sym]:
                        break
                else:
                    if EPSILON not in first[nt]:
                        first[nt].add(EPSILON)
                        changed = True
    return first


def first_of_string(symbols: list[str], first: dict[str, set[str]]) -> set[str]:
    """FIRST of a sequence of symbols (as appears on an RHS)."""
    result: set[str] = set()
    for sym in symbols:
        if sym == EPSILON:
            result.add(EPSILON)
            break
        if is_terminal(sym):
            result.add(sym)
            break
        result |= first[sym] - {EPSILON}
        if EPSILON not in first[sym]:
            break
    else:
        result.add(EPSILON)
    return result


# ---------------------------------------------------------------------------
# 4. FOLLOW set computation
# ---------------------------------------------------------------------------


def compute_follow(first: dict[str, set[str]]) -> dict[str, set[str]]:
    """Return FOLLOW set for every non-terminal."""
    follow: dict[str, set[str]] = {nt: set() for nt in GRAMMAR}
    follow["_start"].add(DOLLAR)

    changed = True
    while changed:
        changed = False
        for nt, alts in GRAMMAR.items():
            for alt in alts:
                for i, sym in enumerate(alt):
                    if not is_nonterminal(sym):
                        continue
                    after = alt[i + 1 :]
                    first_after = first_of_string(after, first)
                    before = len(follow[sym])
                    follow[sym] |= first_after - {EPSILON}
                    if EPSILON in first_after:
                        follow[sym] |= follow[nt]
                    if len(follow[sym]) > before:
                        changed = True
    return follow


# ---------------------------------------------------------------------------
# 5. LL(1) Parsing Table
# ---------------------------------------------------------------------------


def build_parsing_table(
    first: dict[str, set[str]],
    follow: dict[str, set[str]],
) -> dict[str, dict[str, tuple[str, int]]]:
    """Build M[NonTerminal][lexer_token_type] = (production_name, alt_index)."""
    table: dict[str, dict[str, tuple[str, int]]] = {nt: {} for nt in GRAMMAR}

    for nt, alts in GRAMMAR.items():
        for idx, alt in enumerate(alts):
            prod_str = f"{nt} → {' '.join(alt)}"
            first_alpha = first_of_string(alt, first)
            for t in first_alpha:
                if t == EPSILON:
                    continue
                token_types = TERMINAL_TO_TOKEN_TYPES.get(t, {t})
                for tt in token_types:
                    if tt in table[nt]:
                        print(
                            f"  ⚠ CONFLICT in M[{nt}, {tt}]: "
                            f"existing={table[nt][tt][0]}, new={prod_str}"
                        )
                    else:
                        table[nt][tt] = (prod_str, idx)
            if EPSILON in first_alpha:
                for f in follow[nt]:
                    if f == EPSILON:
                        continue
                    token_types = TERMINAL_TO_TOKEN_TYPES.get(f, {f})
                    for tt in token_types:
                        if tt in table[nt]:
                            print(
                                f"  ⚠ CONFLICT in M[{nt}, {tt}]: "
                                f"existing={table[nt][tt][0]}, new={prod_str}"
                            )
                        else:
                            table[nt][tt] = (prod_str, idx)
    return table


# ---------------------------------------------------------------------------
# 6. Table-driven predictive parser
# ---------------------------------------------------------------------------


class LL1Parser:
    """Table-driven LL(1) parser using an explicit stack."""

    def __init__(
        self,
        tokens: list[tuple[str, str]],
        table: dict[str, dict[str, tuple[str, int]]],
        first: dict[str, set[str]],
        follow: dict[str, set[str]],
    ):
        self.tokens = tokens
        self.table = table
        self.first = first
        self.follow = follow
        self.pos = 0
        self.stack: list[str] = [DOLLAR, "_start"]
        self.parse_tree: list[str] = []

    def _current_token_type(self) -> str:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos][0]
        return DOLLAR

    def _current_lexeme(self) -> str:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos][1]
        return DOLLAR

    def _matches_terminal(self, sym: str) -> bool:
        tok_type = self._current_token_type()
        tok_lex = self._current_lexeme()
        # For KEYWORD tokens, the grammar terminal is the lexeme itself
        effective_type = tok_lex if tok_type == "KEYWORD" else tok_type
        allowed_types = TERMINAL_TO_TOKEN_TYPES.get(sym, {sym})
        return effective_type in allowed_types

    def parse(self) -> list[str]:
        """Run the table-driven parser. Returns the list of productions applied."""
        while True:
            top = self.stack[-1]
            a = self._current_token_type()
            lex = self._current_lexeme()

            if top == DOLLAR and a in (DOLLAR, "EOF"):
                return self.parse_tree

            if is_terminal(top):
                if self._matches_terminal(top):
                    self.stack.pop()
                    self.pos += 1
                else:
                    raise SyntaxError(
                        f"Expected terminal '{top}', got {a} '{lex}' at position {self.pos}"
                    )
                continue

            if top in GRAMMAR:
                row = self.table.get(top, {})
                # For KEYWORD tokens, look up by lexeme (e.g. "var", "function")
                lookup_key = lex if a == "KEYWORD" else a
                # For sign non-terminal, distinguish + vs - by lexeme
                if top == "sign" and a == "addop":
                    lookup_key = lex
                entry = row.get(lookup_key)
                if entry is None:
                    if top == "sign":
                        entry = row.get(lex)
                if entry is None:
                    raise SyntaxError(
                        f"No entry in parsing table M[{top}, {a}] "
                        f"at position {self.pos} (lexeme='{lex}', "
                        f"stack top='{top}', stack={self.stack[-3:]})"
                    )
                prod_str, _alt_idx = entry
                self.stack.pop()
                rhs = prod_str.split("→")[1].strip().split()
                rhs = [s for s in rhs if s != EPSILON]
                for sym in reversed(rhs):
                    self.stack.append(sym)
                self.parse_tree.append(prod_str)
                continue

            raise SyntaxError(f"Unknown symbol on stack: {top}")


# ---------------------------------------------------------------------------
# 7. Pretty-printing helpers
# ---------------------------------------------------------------------------


def print_first(first: dict[str, set[str]]) -> None:
    print("=" * 60)
    print("FIRST Sets")
    print("=" * 60)
    for nt in sorted(first):
        syms = ", ".join(sorted(first[nt]))
        print(f"  FIRST({nt:30s}) = {{ {syms} }}")
    print()


def print_follow(follow: dict[str, set[str]]) -> None:
    print("=" * 60)
    print("FOLLOW Sets")
    print("=" * 60)
    for nt in sorted(follow):
        syms = ", ".join(sorted(follow[nt]))
        print(f"  FOLLOW({nt:30s}) = {{ {syms} }}")
    print()


def print_table(table: dict[str, dict[str, tuple[str, int]]]) -> None:
    print("=" * 60)
    print("LL(1) Parsing Table (only non-empty entries)")
    print("=" * 60)
    for nt in sorted(table):
        for tok in sorted(table[nt]):
            prod, _ = table[nt][tok]
            print(f"  M[{nt:30s}, {tok:12s}] = {prod}")
    print()


# ---------------------------------------------------------------------------
# 8. Main
# ---------------------------------------------------------------------------


def main() -> None:
    import sys

    print("Computing FIRST sets ...")
    first = compute_first()
    print_first(first)

    print("Computing FOLLOW sets ...")
    follow = compute_follow(first)
    print_follow(follow)

    print("Building LL(1) parsing table ...")
    table = build_parsing_table(first, follow)
    print_table(table)

    if len(sys.argv) > 1:
        filename = sys.argv[1]
        print(f"\nParsing '{filename}' ...")
        with open(filename) as f:
            lexer = Lexer(f.read())
            tokens = lexer.tokenize()

        parser = LL1Parser(tokens, table, first, follow)
        try:
            productions = parser.parse()
            print("Parsing successful!")
            print(f"  Productions applied: {len(productions)}")
            for p in productions:
                print(f"    {p}")
        except SyntaxError as e:
            print(f"Syntax error: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()
