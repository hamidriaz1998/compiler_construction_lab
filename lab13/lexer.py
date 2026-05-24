KEYWORDS = {
    "program", "var", "array", "of", "integer", "real",
    "function", "procedure", "begin", "end",
    "if", "then", "else", "while", "do",
    "not", "or", "div", "mod", "and",
}

RELOP = {"=", "<>", "<", "<=", ">=", ">"}
ADDOP = {"+", "-", "or"}
MULOP = {"*", "/", "div", "mod", "and"}


class Lexer:
    def __init__(self, source):
        self.source = source
        self.tokens = []
        self.pos = 0
        self.line = 1

    def tokenize(self):
        while self.pos < len(self.source):
            if self.source[self.pos] == "\n":
                self.line += 1
                self.pos += 1
                continue
            if self.source[self.pos].isspace():
                self.pos += 1
                continue
            if self.source[self.pos] == "{":
                while True:
                    if self.source[self.pos] == "\n":
                        self.line += 1
                    self.pos += 1
                    if self.source[self.pos] == "}":
                        self.pos += 1
                        break
                continue
            if self.source[self.pos].isalpha():
                start = self.pos
                while self.pos < len(self.source) and (
                    self.source[self.pos].isalnum() or self.source[self.pos] == "_"
                ):
                    self.pos += 1
                lexeme = self.source[start:self.pos]
                if lexeme in {"div", "mod", "and"}:
                    self.tokens.append(("mulop", lexeme, self.line))
                elif lexeme in KEYWORDS:
                    self.tokens.append(("KEYWORD", lexeme, self.line))
                else:
                    self.tokens.append(("id", lexeme, self.line))
                continue
            if self.source[self.pos].isdigit():
                start = self.pos
                while self.pos < len(self.source) and self.source[self.pos].isdigit():
                    self.pos += 1
                if (
                    self.pos < len(self.source)
                    and self.source[self.pos] == "."
                    and self.pos + 1 < len(self.source)
                    and self.source[self.pos + 1].isdigit()
                ):
                    self.pos += 1
                    while (
                        self.pos < len(self.source) and self.source[self.pos].isdigit()
                    ):
                        self.pos += 1
                self.tokens.append(("num", self.source[start:self.pos], self.line))
                continue
            ch = self.source[self.pos]
            if ch == ":" and self.pos + 1 < len(self.source) and self.source[self.pos + 1] == "=":
                self.tokens.append(("assignop", ":=", self.line))
                self.pos += 2
                continue
            if ch == "<" and self.pos + 1 < len(self.source) and self.source[self.pos + 1] == ">":
                self.tokens.append(("relop", "<>", self.line))
                self.pos += 2
                continue
            if ch in RELOP:
                self.tokens.append(("relop", ch, self.line))
            elif ch in ADDOP:
                self.tokens.append(("addop", ch, self.line))
            elif ch in MULOP:
                self.tokens.append(("mulop", ch, self.line))
            elif ch in {"(", ")", "[", "]", ":", ",", ";", "."}:
                self.tokens.append((ch, ch, self.line))
            else:
                self.pos += 1
                continue
            self.pos += 1
        self.tokens.append(("EOF", "$", self.line))
        return self.tokens


if __name__ == "__main__":
    import sys
    filename = sys.argv[1] if len(sys.argv) > 1 else "source.txt"
    with open(filename) as f:
        source = f.read()
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    for t in tokens:
        print(t)
