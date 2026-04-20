#import "title.typ": title-page

#show: doc => title-page(
  name: "Hamid Riaz",
  reg_no: "2023-CS-10",
  supervisor_name: "Miss Aliya Farooq",
  course_name: "CSC-303L: Compiler Construction Lab",
  title: "Lab 9: Recursive Descent Parsing",
  doc,
)

#pagebreak()

#set list(indent: 1em)
#set enum(indent: 1em)
#set text(size: 12pt)
#show heading: set text(weight: "bold")
#show heading.where(level: 2): set text(size: 16pt)
#show heading.where(level: 3): set text(size: 14pt)

= Pascal Subset Parser (Recursive Descent)
<pascal-subset-parser-recursive-descent>
A recursive-descent parser for a subset of Pascal

== Grammar Transformations
<grammar-transformations>
The original grammar is LALR(1) but not suitable for
recursive-descent/LL(1) parsing due to:

+ #strong[Left Recursion] - eliminated using the standard
  transformation:

  ```
  A → A α | β  ⟹  A → β A'  ,  A' → α A' | ε
  ```

+ #strong[Common Left-Prefix] - eliminated via left factoring:

  ```
  A → α β₁ | α β₂  ⟹  A → α A'  ,  A' → β₁ | β₂
  ```

=== Before/After Examples
<beforeafter-examples>
#strong[identifier\_list] --- left recursion eliminated:

```
Before:
identifier_list  →  id
                 |  identifier_list , id

After:
identifier_list   →  id identifier_list'
identifier_list'  →  , id identifier_list'
                  |  ε
```

#strong[declarations] --- left recursion eliminated (β = ε):

```
Before:
declarations  →  declarations var identifier_list : type ;
           |  ε

After:
declarations   →  declarations'
declarations'  →  var identifier_list : type ; declarations'
               |  ε
```

#strong[statement\_list] --- left recursion eliminated:

```
Before:
statement_list  →  statement
                |  statement_list ; statement

After:
statement_list   →  statement statement_list'
statement_list'  →  ; statement statement_list'
                  |  ε
```

#strong[expression\_list] --- left recursion eliminated:

```
Before:
expression_list  →  expression
                 |  expression_list , expression

After:
expression_list   →  expression expression_list'
expression_list'  →  , expression expression_list'
                  |  ε
```

#strong[simple\_expression] --- left recursion eliminated:

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

#strong[term] --- left recursion eliminated:

```
Before:
term  →  factor
       |  term mulop factor

After:
term   →  factor term'
term'  →  mulop factor term'
        |  ε
```

#strong[expression] --- left factored on `simple_expression`:

```
Before:
expression  →  simple_expression
             |  simple_expression relop simple_expression

After:
expression   →  simple_expression expression'
expression'  →  relop simple_expression
              |  ε
```

#strong[statement] --- left factored on common prefix `id`:

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

#strong[factor] --- left factored on `id`:

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

== Usage
<usage>
=== Tokenize a source file:
<tokenize-a-source-file>
```bash
python3 lexer.py source.pas
```

=== Parse from pre-existing tokens:
<parse-from-pre-existing-tokens>
```bash
python3 lexer.py source.pas > list.txt
python3 parser.py list.txt
```

== Examples
<examples>
Test with included samples:

```bash
python3 lexer.py samples/factorial.pas > tokens.txt && python3 parser.py tokens.txt
python3 lexer.py samples/power.pas > tokens.txt && python3 parser.py tokens.txt
python3 lexer.py samples/max.pas > tokens.txt && python3 parser.py tokens.txt
python3 lexer.py samples/gcd.pas > tokens.txt && python3 parser.py tokens.txt
```

Sample programs in `samples/`:

- `factorial.pas` --- recursive factorial
- `power.pas` --- recursive power
- `max.pas` --- maximum of two numbers
- `gcd.pas` - GCD of two numbers

Output on success:

```
Parsing successful!
```
