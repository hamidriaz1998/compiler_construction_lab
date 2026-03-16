import threading

from buffer_manager import BufferManager, reader


class Token:
    def __init__(self, type_, value):
        self.type = type_
        self.value = value

    def __repr__(self):
        return f"{self.type}({self.value})"


# Simple lookup tables
KEYWORDS = {
    "int": "INT",
    "float": "FLOAT",
    "if": "IF",
    "else": "ELSE",
    "while": "WHILE",
    "return": "RETURN",
    "void": "VOID",
}

OPS = {
    "+": "PLUS",
    "-": "MINUS",
    "*": "STAR",
    "/": "SLASH",
    "=": "EQ",
    "==": "EQEQ",
    "<": "LT",
    ">": "GT",
    "(": "LPAREN",
    ")": "RPAREN",
    "{": "LBRACE",
    "}": "RBRACE",
    ";": "SEMI",
    ",": "COMMA",
}


class Lexer:
    def __init__(self, buf: BufferManager):
        self.buf = buf

    def peek(self):
        """Look at next char without consuming"""
        c = self.buf.get_char()
        if c != "EOF":
            self.buf.unget()
        return c

    def skip_space(self):
        """Skip whitespace"""
        while True:
            c = self.peek()
            if c == "EOF" or not c.isspace():
                break
            self.buf.get_char()

    def read_ident(self):
        """Read identifier or keyword"""
        val = ""
        while True:
            c = self.peek()
            if c == "EOF" or not (c.isalnum() or c == "_"):
                break
            val += self.buf.get_char()

        # Check if keyword
        typ = KEYWORDS.get(val, "IDENT")
        return Token(typ, val)

    def read_number(self):
        """Read number"""
        val = ""
        while True:
            c = self.peek()
            if c == "EOF" or not c.isdigit():
                break
            val += self.buf.get_char()
        return Token("NUM", val)

    def read_op(self):
        """Read operator"""
        c1 = self.buf.get_char()
        c2 = self.peek()

        # Check for 2-char operators
        two = c1 + c2
        if two in OPS:
            self.buf.get_char()  # consume second char
            return Token(OPS[two], two)

        # Single char operator
        if c1 in OPS:
            return Token(OPS[c1], c1)

        return Token("UNKNOWN", c1)

    def next_token(self):
        """Get next token"""
        self.skip_space()
        c = self.peek()

        if c == "EOF":
            return Token("EOF", "")

        if c.isalpha() or c == "_":
            return self.read_ident()

        if c.isdigit():
            return self.read_number()

        return self.read_op()

    def tokenize(self):
        """Tokenize entire input"""
        tokens = []
        while True:
            tok = self.next_token()
            tokens.append(tok)
            if tok.type == "EOF":
                break
        return tokens


def parse_tokens(code="", size=32):
    """Tokenize a string (creates temp file)"""
    import os
    import tempfile

    if code == "":
        with open("test_program.txt") as f:
            code = f.read(1000000)
    # Write to temp file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".c", delete=False) as f:
        f.write(code)
        fname = f.name

    try:
        # Setup double buffer
        buf = BufferManager(size)

        # Start reader thread
        t = threading.Thread(target=reader, args=(fname, buf))
        t.start()

        # Wait for first buffer
        buf.full1.acquire()
        buf.full1.release()

        # Tokenize
        lexer = Lexer(buf)
        tokens = lexer.tokenize()

        t.join()
        return tokens
    finally:
        os.unlink(fname)


# Example usage
if __name__ == "__main__":
    code = """int main() {
        int counter = 0;
        float result = 3.14159;

        while (counter < 1000000) {
            result = result + 0.001;
            counter = counter + 1;
        }

        return 0;
    }"""
    print(f"Reading 1,000,000 chars from test_program.txt with buffer_size 4096")
    print()
    print(f"Tokens: {parse_tokens(size=4096)[:100]}")
    print()

    print(f"Input: {code}")
    print(f"Tokens: {parse_tokens(code[:100])}")
    print()

    code = "int add(int a, int b) { return a + b; }"
    print(f"Input: {code}")
    print(f"Tokens: {parse_tokens(code[:100])}")
    print()

    code = "if (x > 10) { x = x + 10; return 0; }"
    print(f"Input: {code}")
    print(f"Tokens: {parse_tokens(code[:100])}")
