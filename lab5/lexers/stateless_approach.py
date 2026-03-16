from .lexer import KEYWORDS, OPERATORS, Lexer, Token, is_alnum, is_digit, is_letter


class StatelessLexer(Lexer):
    def __init__(self, buffer):
        super().__init__(buffer)

    def skip_whitespace(self):
        while True:
            c = self.get_char()
            match c:
                case " " | "\t" | "\n":
                    continue
                case "{":
                    while True:
                        c = self.get_char()
                        if c == "EOF":
                            return
                        if c == "}":
                            break
                    continue
                case "EOF":
                    return
                case _:
                    self.unget()
                    return

    def scan_identifier(self):
        lexeme = ""
        c = self.get_char()

        while is_alnum(c):
            lexeme += c
            c = self.get_char()

        self.unget()

        token_type = KEYWORDS.get(lexeme.lower(), "ID")
        return Token(token_type, lexeme, self.line)

    def scan_number(self):
        lexeme = ""
        c = self.get_char()

        while is_digit(c):
            lexeme += c
            c = self.get_char()

        if c == ".":
            lexeme += c
            c = self.get_char()

            while is_digit(c):
                lexeme += c
                c = self.get_char()

            self.unget()
            return Token("REAL", lexeme, self.line)

        self.unget()
        return Token("INTEGER", lexeme, self.line)

    def scan_operator(self):
        c = self.get_char()

        match c:
            case ":":
                n = self.get_char()
                if n == "=":
                    return Token("ASSIGN", ":=", self.line)
                self.unget()
                return Token("COLON", ":", self.line)

            case "<":
                n = self.get_char()

                match n:
                    case "=":
                        return Token("LE", "<=", self.line)
                    case ">":
                        return Token("NE", "<>", self.line)
                    case _:
                        self.unget()
                        return Token("LT", "<", self.line)

            case ">":
                n = self.get_char()

                if n == "=":
                    return Token("GE", ">=", self.line)

                self.unget()
                return Token("GT", ">", self.line)

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

    def next_token(self):
        self.skip_whitespace()

        c = self.get_char()

        if c == "EOF":
            return Token("EOF", "", self.line)

        self.unget()

        if is_letter(c):
            return self.scan_identifier()

        if is_digit(c):
            return self.scan_number()

        return self.scan_operator()
