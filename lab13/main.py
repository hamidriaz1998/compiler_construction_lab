import sys

from lexer import Lexer
from symbol_table import SymbolTable
from parser import PascalRecursiveDescentParser


def main():
    filename = sys.argv[1] if len(sys.argv) > 1 else "source.pas"

    with open(filename) as f:
        source = f.read()

    lexer = Lexer(source)
    tokens = lexer.tokenize()

    print("Tokens:")
    for t in tokens:
        print(f"  {t}")
    print()

    global_table = SymbolTable(scope_level=0)
    parser = PascalRecursiveDescentParser(tokens, global_table)

    try:
        parser.parse()
        print("\nFinal symbol table (global scope):")
        global_table.print()
    except SyntaxError as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
