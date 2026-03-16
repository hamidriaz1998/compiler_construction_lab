from dataclasses import dataclass

from buffer_manager import BufferManager

KEYWORDS = {
    "program": "PROGRAM",
    "var": "VAR",
    "array": "ARRAY",
    "of": "OF",
    "integer": "INTEGER_TYPE",
    "real": "REAL_TYPE",
    "function": "FUNCTION",
    "procedure": "PROCEDURE",
    "begin": "BEGIN",
    "end": "END",
    "if": "IF",
    "then": "THEN",
    "else": "ELSE",
    "while": "WHILE",
    "do": "DO",
    "not": "NOT",
}

OPERATORS = {
    "+": "PLUS",
    "-": "MINUS",
    "*": "MULT",
    "/": "DIV",
    "=": "EQ",
    "(": "LPAREN",
    ")": "RPAREN",
    "[": "LBRACKET",
    "]": "RBRACKET",
    ";": "SEMICOLON",
    ",": "COMMA",
}


@dataclass
class Token:
    type: str
    value: str
    line: int


# Helpers
def is_letter(c):
    return c.isalpha()


def is_digit(c):
    return c.isdigit()


def is_alnum(c):
    return c.isalnum()


# Base Lexer class
class Lexer:
    def __init__(self, buffer: BufferManager):
        self.buffer = buffer
        self.line = 1
        self.current = ""

    def get_char(self):
        ch = self.buffer.get_char()

        if ch == "\n":
            self.line += 1

        return ch

    def unget(self):
        self.buffer.unget()
