class PascalRecursiveDescentParser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.lookahead = tokens[0] if tokens else ("EOF", "$")

    def consume(self):
        self.pos += 1
        if self.pos < len(self.tokens):
            self.lookahead = self.tokens[self.pos]
        else:
            self.lookahead = ("EOF", "$")

    # ---------- token helpers ----------
    def token_is(self, symbol):
        """True if current token type OR lexeme equals symbol."""
        return self.lookahead[0] == symbol or self.lookahead[1] == symbol

    def token_in(self, symbols):
        return any(self.token_is(s) for s in symbols)

    def match(self, token_type):
        if self.token_is(token_type):
            self.consume()
        else:
            raise SyntaxError(f"Expected {token_type}, got {self.lookahead}")

    # ==================== GRAMMAR RULES ====================

    def parse(self):
        self.program()
        if self.lookahead[0] != "EOF":
            raise SyntaxError(f"Unexpected token after parsing: {self.lookahead}")
        print("Parsing successful!")

    # program → program id ( identifier_list ) ; declarations subprogram_declarations compound_statement
    def program(self):
        self.match("program")
        self.match("id")
        self.match("(")
        self.identifier_list()
        self.match(")")
        self.match(";")
        self.declarations()
        self.subprogram_declarations()
        self.compound_statement()

    # identifier_list → id identifier_list'
    def identifier_list(self):
        self.match("id")
        self.identifier_list_prime()

    # identifier_list' → , id identifier_list' | ε
    def identifier_list_prime(self):
        if self.token_is(","):
            self.match(",")
            self.match("id")
            self.identifier_list_prime()

    # declarations → var identifier_list : type ; declarations | ε
    def declarations(self):
        if self.token_is("var"):
            self.match("var")
            self.identifier_list()
            self.match(":")
            self.type_()
            self.match(";")
            self.declarations()

    # type → standard_type | array [ num .. num ] of standard_type
    def type_(self):
        if self.token_is("array"):
            self.match("array")
            self.match("[")
            self.match("num")
            # Lexer tokenizes ".." as two "." tokens, so consume "." twice.
            self.match(".")
            self.match(".")
            self.match("num")
            self.match("]")
            self.match("of")
            self.standard_type()
        else:
            self.standard_type()

    # standard_type → integer | real
    def standard_type(self):
        if self.token_in(("integer", "real")):
            if self.token_is("integer"):
                self.match("integer")
            else:
                self.match("real")
        else:
            raise SyntaxError(f"Expected 'integer' or 'real', got {self.lookahead}")

    # subprogram_declarations → subprogram_declaration ; subprogram_declarations | ε
    def subprogram_declarations(self):
        if self.token_in(("function", "procedure")):
            self.subprogram_declaration()
            self.match(";")
            self.subprogram_declarations()

    # subprogram_declaration → subprogram_head declarations compound_statement
    def subprogram_declaration(self):
        self.subprogram_head()
        self.declarations()
        self.compound_statement()

    # subprogram_head → function id arguments : standard_type ; | procedure id arguments ;
    def subprogram_head(self):
        if self.token_is("function"):
            self.match("function")
            self.match("id")
            self.arguments()
            self.match(":")
            self.standard_type()
            self.match(";")
        elif self.token_is("procedure"):
            self.match("procedure")
            self.match("id")
            self.arguments()
            self.match(";")
        else:
            raise SyntaxError(
                f"Expected 'function' or 'procedure', got {self.lookahead}"
            )

    # arguments → ( parameter_list ) | ε
    def arguments(self):
        if self.token_is("("):
            self.match("(")
            self.parameter_list()
            self.match(")")

    # parameter_list → identifier_list : type parameter_list'
    def parameter_list(self):
        self.identifier_list()
        self.match(":")
        self.type_()
        self.parameter_list_prime()

    # parameter_list' → ; identifier_list : type parameter_list' | ε
    def parameter_list_prime(self):
        if self.token_is(";"):
            self.match(";")
            self.identifier_list()
            self.match(":")
            self.type_()
            self.parameter_list_prime()

    # compound_statement → begin optional_statements end
    def compound_statement(self):
        self.match("begin")
        self.optional_statements()
        self.match("end")

    # optional_statements → statement_list | ε
    def optional_statements(self):
        if self.token_in(("id", "if", "while", "begin")):
            self.statement_list()

    # statement_list → statement statement_list'
    def statement_list(self):
        self.statement()
        self.statement_list_prime()

    # statement_list' → ; statement statement_list' | ε
    def statement_list_prime(self):
        if self.token_is(";"):
            self.match(";")
            self.statement()
            self.statement_list_prime()

    # statement → id statement_tail | compound_statement
    #            | if expression then statement else statement
    #            | while expression do statement
    def statement(self):
        if self.token_is("id"):
            self.match("id")
            self.statement_tail()
        elif self.token_is("begin"):
            self.compound_statement()
        elif self.token_is("if"):
            self.match("if")
            self.expression()
            self.match("then")
            self.statement()
            self.match("else")
            self.statement()
        elif self.token_is("while"):
            self.match("while")
            self.expression()
            self.match("do")
            self.statement()
        else:
            raise SyntaxError(f"Unexpected token in statement: {self.lookahead}")

    # statement_tail → assignop expression
    #                | [ expression ] assignop expression
    #                | ( expression_list )
    #                | ε
    def statement_tail(self):
        if self.token_is("["):
            self.match("[")
            self.expression()
            self.match("]")
            self.match("assignop")
            self.expression()
        elif self.token_is("("):
            self.match("(")
            self.expression_list()
            self.match(")")
        elif self.token_is("assignop"):
            self.match("assignop")
            self.expression()
        else:
            pass  # ε

    # variable → id variable'
    def variable(self):
        self.match("id")
        self.variable_prime()

    # variable' → [ expression ] | ε
    def variable_prime(self):
        if self.token_is("["):
            self.match("[")
            self.expression()
            self.match("]")

    # procedure_statement → id procedure_statement'
    def procedure_statement(self):
        self.match("id")
        self.procedure_statement_prime()

    # procedure_statement' → ( expression_list ) | ε
    def procedure_statement_prime(self):
        if self.token_is("("):
            self.match("(")
            self.expression_list()
            self.match(")")

    # expression_list → expression expression_list'
    def expression_list(self):
        self.expression()
        self.expression_list_prime()

    # expression_list' → , expression expression_list' | ε
    def expression_list_prime(self):
        if self.token_is(","):
            self.match(",")
            self.expression()
            self.expression_list_prime()

    # expression → simple_expression | simple_expression relop simple_expression
    def expression(self):
        self.simple_expression()
        if self.token_is("relop"):
            self.match("relop")
            self.simple_expression()

    # simple_expression → term simple_expression' | sign term simple_expression'
    def simple_expression(self):
        if self.token_in(("+", "-")):
            self.sign()
            self.term()
            self.simple_expression_prime()
        else:
            self.term()
            self.simple_expression_prime()

    # simple_expression' → addop term simple_expression' | ε
    def simple_expression_prime(self):
        if self.token_is("addop"):
            self.match("addop")
            self.term()
            self.simple_expression_prime()

    # sign → + | -
    # Lexer classifies + and - as addop tokens, so verify lexeme.
    def sign(self):
        if self.lookahead[0] == "addop" and self.lookahead[1] in ("+", "-"):
            self.consume()
        else:
            raise SyntaxError(f"Expected unary '+' or '-', got {self.lookahead}")

    # term → factor term'
    def term(self):
        self.factor()
        self.term_prime()

    # term' → mulop factor term' | ε
    def term_prime(self):
        if self.token_is("mulop"):
            self.match("mulop")
            self.factor()
            self.term_prime()

    # factor → id factor' | num | ( expression ) | not factor
    def factor(self):
        if self.token_is("id"):
            self.match("id")
            self.factor_prime()
        elif self.token_is("num"):
            self.match("num")
        elif self.token_is("("):
            self.match("(")
            self.expression()
            self.match(")")
        elif self.token_is("not"):
            self.match("not")
            self.factor()
        else:
            raise SyntaxError(f"Unexpected token in factor: {self.lookahead}")

    # factor' → ( expression_list ) | ε
    def factor_prime(self):
        if self.token_is("("):
            self.match("(")
            self.expression_list()
            self.match(")")


if __name__ == "__main__":
    import ast
    import sys

    filename = sys.argv[1] if len(sys.argv) > 1 else "list.txt"
    with open(filename) as f:
        tokens = ast.literal_eval(f.read())
    parser = PascalRecursiveDescentParser(tokens)
    parser.parse()
