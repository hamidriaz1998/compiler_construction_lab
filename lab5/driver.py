import argparse
import sys

from buffer_manager import BufferManager


def main():
    parser = argparse.ArgumentParser(
        description="Lexical analyzer for Pascal-like language"
    )
    parser.add_argument("filename", help="Input file to tokenize")
    parser.add_argument(
        "--lexer",
        choices=["state", "stateless", "table"],
        default="state",
        help="Type of lexer to use (default: state)",
    )
    parser.add_argument(
        "--rich", action="store_true", help="Output token stream as a rich table"
    )

    args = parser.parse_args()

    # Initialize buffer manager
    buffer = BufferManager()

    # Read the file content
    try:
        with open(args.filename, "r") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: File '{args.filename}' not found.")
        sys.exit(1)

    # Fill buffer with content
    buffer.fill(1, content)

    # Setup buffer for reading (active buffer 1, start at position 0)
    buffer.active = 1
    buffer.forward = 0
    buffer.done = True  # Mark as done since we've filled the buffer

    # Select lexer based on argument
    if args.lexer == "state":
        from lexers.state_approach import StateApproachLexer

        lexer = StateApproachLexer(buffer)
    elif args.lexer == "stateless":
        from lexers.stateless_approach import StatelessLexer

        lexer = StatelessLexer(buffer)
    else:  # table
        from lexers.table_approach import TableLexer

        lexer = TableLexer(buffer)

    # Tokenize and collect tokens
    tokens = []
    while True:
        token = lexer.next_token()
        if token.type == "EOF":
            break
        tokens.append(token)

    if args.rich:
        # Output as rich table
        try:
            from rich.console import Console
            from rich.table import Table
        except ImportError:
            print(
                "Error: rich package is required for --rich option. Install it with: pip install rich"
            )
            sys.exit(1)

        console = Console()
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Line", style="dim", width=6)
        table.add_column("Token Type", width=12)
        table.add_column("Lexeme", width=10)
        table.add_column("Value", width=8)

        for token in tokens:
            # Determine value to display
            if token.type in ["INTEGER", "REAL"]:
                value = token.value
            else:
                value = "-"

            table.add_row(str(token.line), token.type, token.value, value)

        console.print(table)
        console.print(f"[bold]Total Tokens:[/bold] {len(tokens)}")
    else:
        # Print token stream in required format
        print("Token Stream:")
        print("-----------------------------------------")
        print("Line | Token Type | Lexeme | Value")
        print("-----------------------------------------")

        for token in tokens:
            # Determine value to display
            if token.type in ["INTEGER", "REAL"]:
                value = token.value
            else:
                value = "-"

            print(f"{token.line:4} | {token.type:10} | {token.value:8} | {value}")

        print("-----------------------------------------")
        print(f"Total Tokens: {len(tokens)}")


if __name__ == "__main__":
    main()
