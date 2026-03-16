from .lexer import KEYWORDS, OPERATORS, Lexer, Token, is_alnum, is_digit, is_letter


class StateApproachLexer(Lexer):
    def __init__(self, buffer):
        super().__init__(buffer)

    def next_token(self):
        state = "START"
        lexeme = ""

        while True:
            c = self.get_char()

            match state:
                case "START":
                    if c in [" ", "\t", "\n"]:
                        continue

                    if c == "EOF":
                        return Token("EOF", "", self.line)

                    if is_letter(c):
                        lexeme += c
                        state = "IN_ID"
                        continue

                    if is_digit(c):
                        lexeme += c
                        state = "IN_NUM"
                        continue

                    match c:
                        case "{":
                            state = "COMMENT"

                        case ":":
                            state = "ASSIGN"

                        case "<":
                            state = "LT"

                        case ">":
                            state = "GT"

                        case ".":
                            n = self.get_char()
                            if n == ".":
                                return Token("DOTDOT", "..", self.line)
                            self.unget()
                            return Token("DOT", ".", self.line)

                        case _:
                            if c in OPERATORS:
                                return Token(OPERATORS[c], c, self.line)

                            return Token("UNKNOWN", c, self.line)

                case "IN_ID":
                    if is_alnum(c):
                        lexeme += c
                        continue

                    self.unget()

                    token_type = KEYWORDS.get(lexeme.lower(), "ID")
                    return Token(token_type, lexeme, self.line)

                case "IN_NUM":
                    if is_digit(c):
                        lexeme += c
                        continue

                    if c == ".":
                        lexeme += c
                        state = "REAL"
                        continue

                    self.unget()
                    return Token("INTEGER", lexeme, self.line)

                case "REAL":
                    if is_digit(c):
                        lexeme += c
                        continue

                    self.unget()
                    return Token("REAL", lexeme, self.line)

                case "ASSIGN":
                    if c == "=":
                        return Token("ASSIGN", ":=", self.line)

                    self.unget()
                    return Token("COLON", ":", self.line)

                case "LT":
                    match c:
                        case "=":
                            return Token("LE", "<=", self.line)
                        case ">":
                            return Token("NE", "<>", self.line)
                        case _:
                            self.unget()
                            return Token("LT", "<", self.line)

                case "GT":
                    if c == "=":
                        return Token("GE", ">=", self.line)

                    self.unget()
                    return Token("GT", ">", self.line)

                case "COMMENT":
                    if c == "}":
                        state = "START"
