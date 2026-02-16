class Token:
    def __init__(self, type: str, value: float | str):
        self.type = type
        self.value = value

    def __repr__(self):
        return f"{self.type}:{self.value}"


token_types_lookup = {
    "+": "PLUS",
    "-": "MINUS",
    "*": "MULTIPLY",
    "/": "DIVIDE",
    "(": "LPAREN",
    ")": "RPAREN",
    "=": "ASSIGN",
}


def parse_tokens(expr: str) -> list[Token]:
    tokens: list[Token] = []
    lparen_count = 0
    i = 0

    while i < len(expr):
        ch = expr[i]

        if ch.isspace():
            i += 1
            continue

        if ch.isdigit() or (ch == "." and i + 1 < len(expr) and expr[i + 1].isdigit()):
            start = i
            seen_dot = False
            while i < len(expr) and (expr[i].isdigit() or expr[i] == "."):
                if expr[i] == ".":
                    if seen_dot:
                        raise Exception("Syntax Error: Invalid number format")
                    seen_dot = True
                i += 1
            tokens.append(Token("NUMBER", float(expr[start:i])))
            continue

        if ch.isalpha() or ch == "_":
            start = i
            i += 1
            while i < len(expr) and (expr[i].isalnum() or expr[i] == "_"):
                i += 1
            tokens.append(Token("IDENTIFIER", expr[start:i]))
            continue

        if ch in token_types_lookup:
            tokens.append(Token(token_types_lookup[ch], ch))
            i += 1
        else:
            raise Exception(f"Syntax Error: Invalid character '{ch}'")

        if tokens[-1].type == "LPAREN":
            lparen_count += 1
        elif tokens[-1].type == "RPAREN":
            lparen_count -= 1
            if lparen_count < 0:
                raise Exception("Syntax Error: Unmatched parentheses")

    if lparen_count != 0:
        raise Exception("Syntax Error: Unmatched parentheses")

    return tokens
