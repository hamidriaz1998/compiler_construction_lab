# Pascal Subset Parser (Recursive Descent)

A recursive-descent parser for a subset of Pascal

## Grammar Transformations

The original grammar is LALR(1) but not suitable for recursive-descent/LL(1) parsing due to:

1. **Left Recursion** - eliminated using the standard transformation:

   ```
   A → A α | β  ⟹  A → β A'  ,  A' → α A' | ε
   ```

2. **Common Left-Prefix** - eliminated via left factoring:
   ```
   A → α β₁ | α β₂  ⟹  A → α A'  ,  A' → β₁ | β₂
   ```

### Before/After Examples

**identifier_list** — left recursion eliminated:

```
Before:
identifier_list  →  id
                 |  identifier_list , id

After:
identifier_list   →  id identifier_list'
identifier_list'  →  , id identifier_list'
                  |  ε
```

**declarations** — left recursion eliminated (β = ε):

```
Before:
declarations  →  declarations var identifier_list : type ;
           |  ε

After:
declarations   →  declarations'
declarations'  →  var identifier_list : type ; declarations'
               |  ε
```

**statement_list** — left recursion eliminated:

```
Before:
statement_list  →  statement
                |  statement_list ; statement

After:
statement_list   →  statement statement_list'
statement_list'  →  ; statement statement_list'
                  |  ε
```

**expression_list** — left recursion eliminated:

```
Before:
expression_list  →  expression
                 |  expression_list , expression

After:
expression_list   →  expression expression_list'
expression_list'  →  , expression expression_list'
                  |  ε
```

**simple_expression** — left recursion eliminated:

```
Before:
simple_expression  →  term
                    |  sign term
                    |  simple_expression addop term

After:
simple_expression   →  term simple_expression'
                     |  sign term simple_expression'
simple_expression'  →  addop term simple_expression'
                     |  ε
```

**term** — left recursion eliminated:

```
Before:
term  →  factor
       |  term mulop factor

After:
term   →  factor term'
term'  →  mulop factor term'
        |  ε
```

**expression** — left factored on `simple_expression`:

```
Before:
expression  →  simple_expression
             |  simple_expression relop simple_expression

After:
expression   →  simple_expression expression'
expression'  →  relop simple_expression
              |  ε
```

**statement** — left factored on common prefix `id`:

```
Before:
statement  →  variable assignop expression
            |  procedure_statement
            |  compound_statement
            ...

After:
statement      →  id statement_tail
                |  compound_statement
                |  if expression then statement else statement
                |  while expression do statement

statement_tail →  assignop expression
                |  [ expression ] assignop expression
                |  ( expression_list )
                |  ε
```

**factor** — left factored on `id`:

```
Before:
factor  →  id
        |  id ( expression_list )
        |  num
        |  ( expression )
        |  not factor

After:
factor   →  id factor'
          |  num
          |  ( expression )
          |  not factor
factor'  →  ( expression_list )
          |  ε
```

## Usage

### Tokenize a source file:

```bash
python3 lexer.py source.pas
```

### Parse from pre-existing tokens:

```bash
python3 lexer.py source.pas > list.txt
python3 parser.py list.txt
```

## Examples

Test with included samples:

```bash
python3 lexer.py samples/factorial.pas > tokens.txt && python3 parser.py tokens.txt
python3 lexer.py samples/power.pas > tokens.txt && python3 parser.py tokens.txt
python3 lexer.py samples/max.pas > tokens.txt && python3 parser.py tokens.txt
python3 lexer.py samples/gcd.pas > tokens.txt && python3 parser.py tokens.txt
```

Sample programs in `samples/`:

- `factorial.pas` — recursive factorial
- `power.pas` — recursive power
- `max.pas` — maximum of two numbers
- `gcd.pas` - GCD of two numbers

Output on success:

```
Parsing successful!
```
