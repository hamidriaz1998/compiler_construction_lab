from task1 import parse_tokens
from task3 import evaluate_expr

if __name__ == "__main__":
    inputs = []
    with open("inputs.txt") as f:
        inputs = f.readlines()

    for expr in inputs:
        cleaned = expr.strip()
        tokens = parse_tokens(cleaned)
        print("Expression: " + cleaned)
        print(f"Tokens: {tokens}")
        print(f"Result: {evaluate_expr(tokens)}")
