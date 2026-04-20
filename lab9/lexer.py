KEYWORDS = {
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

RELOP = {"=", "<>", "<", "<=", ">=", ">"}
ADDOP = {"+", "-", "or"}
MULOP = {"*", "/", "div", "mod", "and"}


class Lexer:
    def __init__(self, source):
        self.source = source
        self.tokens = []
        self.pos = 0

    def tokenize(self):
        while self.pos < len(self.source):
            if self.source[self.pos].isspace():
                # Skip spaces
                self.pos += 1
                continue
            if self.source[self.pos] == "{":
                # Skip comments
                while True:
                    self.pos += 1
                    if self.source[self.pos] == "}":
                        break
            if self.source[self.pos].isalpha():
                start = self.pos
                while self.pos < len(self.source) and (
                    self.source[self.pos].isalnum() or self.source[self.pos] == "_"
                ):
                    self.pos += 1
                lexeme = self.source[start : self.pos]
                if lexeme in {"div", "mod", "and"}:
                    self.tokens.append(("mulop", lexeme))
                elif lexeme in KEYWORDS:
                    self.tokens.append(("KEYWORD", lexeme))
                else:
                    self.tokens.append(("id", lexeme))
                continue
            if self.source[self.pos].isdigit():
                start = self.pos
                while self.pos < len(self.source) and self.source[self.pos].isdigit():
                    self.pos += 1
                if self.source[self.pos] == ".":
                    self.pos += 1
                    while (
                        self.pos < len(self.source) and self.source[self.pos].isdigit()
                    ):
                        self.pos += 1
                self.tokens.append(("num", self.source[start : self.pos]))
                continue
            if (
                self.source[self.pos] in RELOP
                or self.source[self.pos] in ADDOP
                or self.source[self.pos] in MULOP
                or self.source[self.pos] in {"(", ")", "[", "]", ":", ",", ";", "."}
            ):
                char = self.source[self.pos]
                if (
                    char == ":"
                    and self.pos + 1 < len(self.source)
                    and self.source[self.pos + 1] == "="
                ):
                    self.tokens.append(("assignop", ":="))
                    self.pos += 2
                    continue
                if (
                    char == "<"
                    and self.pos + 1 < len(self.source)
                    and self.source[self.pos + 1] == ">"
                ):
                    self.tokens.append(("relop", "<>"))
                    self.pos += 2
                    continue
                if char in RELOP:
                    self.tokens.append(("relop", char))
                elif char in ADDOP:
                    self.tokens.append(("addop", char))
                elif char in MULOP:
                    self.tokens.append(("mulop", char))
                elif char in {"(", ")", "[", "]", ":", ",", ";", "."}:
                    self.tokens.append((char, char))
                self.pos += 1
                continue
            self.pos += 1
        self.tokens.append(("EOF", "$"))
        return self.tokens


if __name__ == "__main__":
    import sys

    filename = sys.argv[1] if len(sys.argv) > 1 else "source.txt"
    with open(filename) as f:
        source = f.read()
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    print(tokens)
