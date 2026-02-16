from task1 import Token

# Persist variable bindings across evaluations
symbol_table: dict[str, float] = {}


def evaluate_expr(tokens: list[Token]) -> float:
    def parse_factor(idx: int) -> tuple[float, int]:
        tok = tokens[idx]
        if tok.type == "NUMBER":
            return float(tok.value), idx + 1
        if tok.type == "IDENTIFIER":
            if tok.value not in symbol_table:
                raise Exception(f"Undefined variable '{tok.value}'")
            return float(symbol_table[tok.value]), idx + 1
        if tok.type == "LPAREN":
            value, next_idx = parse_expr(idx + 1)
            if next_idx >= len(tokens) or tokens[next_idx].type != "RPAREN":
                raise Exception("Syntax Error: Unmatched parentheses")
            return value, next_idx + 1
        raise Exception(f"Syntax Error: Unexpected token {tok}")

    def parse_term(idx: int) -> tuple[float, int]:
        value, idx = parse_factor(idx)
        while idx < len(tokens) and tokens[idx].type in ("MULTIPLY", "DIVIDE"):
            op = tokens[idx].type
            rhs, idx = parse_factor(idx + 1)
            if op == "MULTIPLY":
                value *= rhs
            else:
                value /= rhs
        return value, idx

    def parse_expr(idx: int) -> tuple[float, int]:
        value, idx = parse_term(idx)
        while idx < len(tokens) and tokens[idx].type in ("PLUS", "MINUS"):
            op = tokens[idx].type
            rhs, idx = parse_term(idx + 1)
            if op == "PLUS":
                value += rhs
            else:
                value -= rhs
        return value, idx

    # Handle assignment: IDENTIFIER ASSIGN <expr>
    if len(tokens) >= 3 and tokens[0].type == "IDENTIFIER" and tokens[1].type == "ASSIGN":
        value, next_idx = parse_expr(2)
        if next_idx != len(tokens):
            raise Exception("Syntax Error: Extra tokens after assignment")
        symbol_table[tokens[0].value] = value
        return value

    value, next_idx = parse_expr(0)
    if next_idx != len(tokens):
        raise Exception("Syntax Error: Extra tokens after expression")
    return value
    