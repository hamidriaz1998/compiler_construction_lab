from .lexer import KEYWORDS, OPERATORS, Lexer, Token


class CharClass:
    LETTER = 0
    DIGIT = 1
    WHITESPACE = 2
    DOT = 3
    COLON = 4
    LT = 5
    GT = 6
    OPERATOR = 7
    OTHER = 8


def classify(c):
    # Sentinel guard
    if c == "EOF":
        return CharClass.OTHER

    if c.isalpha():
        return CharClass.LETTER

    if c.isdigit():
        return CharClass.DIGIT

    if c in " \t\n":
        return CharClass.WHITESPACE

    if c == ".":
        return CharClass.DOT

    if c == ":":
        return CharClass.COLON

    if c == "<":
        return CharClass.LT

    if c == ">":
        return CharClass.GT

    if c in OPERATORS:
        return CharClass.OPERATOR

    return CharClass.OTHER


# states:
# 0 = START
# 1 = ID
# 2 = INTEGER
# 3 = REAL
# 4 = COLON
# 5 = LT
# 6 = GT
#
# -1 = stop / accept

transitionTable = [
    # L  D  WS  .  :  <  >  OP  OTH
    [1, 2, 0, -1, 4, 5, 6, -1, -1],  # 0 START
    [1, 1, -1, -1, -1, -1, -1, -1, -1],  # 1 ID
    [-1, 2, -1, 3, -1, -1, -1, -1, -1],  # 2 INTEGER
    [-1, 3, -1, -1, -1, -1, -1, -1, -1],  # 3 REAL
    [-1, -1, -1, -1, -1, -1, -1, -1, -1],  # 4 COLON
    [-1, -1, -1, -1, -1, -1, -1, -1, -1],  # 5 LT
    [-1, -1, -1, -1, -1, -1, -1, -1, -1],  # 6 GT
]

ACCEPTING = {1: "ID", 2: "INTEGER", 3: "REAL"}


class TableLexer(Lexer):
    def __init__(self, buffer):
        super().__init__(buffer)

    def skip_comment(self):
        while True:
            c = self.get_char()
            if c == "}" or c == "EOF":
                return

    def next_token(self):
        while True:
            c = self.get_char()
            if c == "EOF":
                return Token("EOF", "", self.line)
            if c in (" ", "\t", "\n"):
                continue
            if c == "{":
                self.skip_comment()
                continue
            break

        cls = classify(c)

        if cls in (CharClass.LETTER, CharClass.DIGIT):
            state = transitionTable[0][cls]
            lexeme = c

            while True:
                c = self.get_char()
                if c == "EOF":
                    token_type = ACCEPTING[state]
                    if token_type == "ID":
                        token_type = KEYWORDS.get(lexeme.lower(), "ID")
                    return Token(token_type, lexeme, self.line)

                cls = classify(c)
                next_state = transitionTable[state][cls]

                if next_state == -1:
                    self.unget()
                    token_type = ACCEPTING[state]
                    if token_type == "ID":
                        token_type = KEYWORDS.get(lexeme.lower(), "ID")
                    return Token(token_type, lexeme, self.line)

                lexeme += c
                state = next_state

        if c == ":":
            n = self.get_char()
            if n == "=":
                return Token("ASSIGN", ":=", self.line)
            if n != "EOF":
                self.unget()
            return Token("COLON", ":", self.line)

        if c == "<":
            n = self.get_char()
            if n == "=":
                return Token("LE", "<=", self.line)
            if n == ">":
                return Token("NE", "<>", self.line)
            if n != "EOF":
                self.unget()
            return Token("LT", "<", self.line)

        if c == ">":
            n = self.get_char()
            if n == "=":
                return Token("GE", ">=", self.line)
            if n != "EOF":
                self.unget()
            return Token("GT", ">", self.line)

        if c == ".":
            n = self.get_char()
            if n == ".":
                return Token("DOTDOT", "..", self.line)
            if n != "EOF":
                self.unget()
            return Token("DOT", ".", self.line)

        if c in OPERATORS:
            return Token(OPERATORS[c], c, self.line)

        return Token("UNKNOWN", c, self.line)
