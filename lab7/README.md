# Lab7: Pascal Lexer

## Overview

This lab implements a **lexical analyzer (lexer)** for the **Pascal programming language** using Flex (Fast Lexical Analyzer Generator). The lexer tokenizes Pascal source code by recognizing keywords, identifiers, operators, delimiters, and literals, then outputs the corresponding token types.

## About Pascal

Pascal is a procedural programming language created in the 1970s by Niklaus Wirth. It was designed to be easy to learn and encourage good programming practices. Key characteristics include:

- **Structured Programming**: Uses procedures and modular code design
- **Static Typing**: Variables must be declared with explicit types (integer, real, etc.)
- **Pascal Syntax**: Uses keywords like `program`, `var`, `begin`, `end`, `if`, `while`, etc.
- **Array Support**: Includes array data structures with range specifications
- **Comments**: Uses curly braces `{ ... }` for comments

This lexer specifically recognizes and tokenizes a subset of Pascal suitable for simple programs with:

- Variable declarations
- Integer and real number literals
- Control flow statements (if/then/else, while/do)
- Arithmetic operations
- Assignment and comparison operators

## Compilation Instructions

### Prerequisites

- **Flex** (Fast Lexical Analyzer Generator)
- **GCC** or another C compiler

### Build Steps

```bash
# Navigate to the lab7 directory
cd compiler_construction/lab7

# Generate C code from the Flex specification
flex lexer.l

# Compile the generated C code
gcc lex.yy.c -o lexer
```

Or use a single command:

```bash
flex lexer.l && gcc lex.yy.c -o lexer
```

## Execution with Examples

### Example 1: Simple Pascal Program

**Input file: `sample1.pas`**

```pascal
program sample1;

{ This is a sample program }

var
    x : integer;

begin
    x := 1;
end.
```

**Run the lexer:**

```bash
./lexer < sample1.pas
```

**Output:**

```
PROGRAM
ID(sample1)
SEMICOLON
VAR
ID(x)
COLON
INTEGER_TYPE
SEMICOLON
BEGIN
ID(x)
ASSIGN
INTEGER(1)
SEMICOLON
END
DOT
```

### Example 2: Program with Multiple Variables

**Input file: `sample2.pas`**

```pascal
program sample2;

var
    a : integer;
    b: integer;

begin
    a := 2;
    b := 3;
    a := a + b;
end.
```

**Run the lexer:**

```bash
./lexer < sample2.pas
```

**Output:**

```
PROGRAM
ID(sample2)
SEMICOLON
VAR
ID(a)
COLON
INTEGER_TYPE
SEMICOLON
ID(b)
COLON
INTEGER_TYPE
SEMICOLON
BEGIN
ID(a)
ASSIGN
INTEGER(2)
SEMICOLON
ID(b)
ASSIGN
INTEGER(3)
SEMICOLON
ID(a)
ASSIGN
ID(a)
PLUS
INTEGER(b)
SEMICOLON
END
DOT
```

### Example 3: Create Your Own Test File

Create a new Pascal file (e.g., `test.pas`):

```pascal
program test;

var
    count : integer;
    value : real;

begin
    count := 5;
    value := 3.14;
    if count > 0 then
        count := count - 1;
end.
```

Run the lexer:

```bash
./lexer < test.pas
```

## Token Reference

The lexer recognizes the following tokens:

### Keywords

- `PROGRAM` - Program declaration
- `VAR` - Variable declaration section
- `INTEGER_TYPE` - Integer type keyword
- `REAL_TYPE` - Real type keyword
- `ARRAY` - Array declaration
- `OF` - Used with arrays
- `BEGIN` - Start of code block
- `END` - End of code block
- `IF` - Conditional statement
- `THEN` - Part of if statement
- `ELSE` - Alternative branch
- `WHILE` - Loop statement
- `DO` - Part of while loop
- `NOT` - Logical negation

### Operators

- `ASSIGN` `:=` - Assignment
- `PLUS` `+` - Addition
- `MINUS` `-` - Subtraction
- `MULT` `*` - Multiplication
- `DIV` `/` - Division
- `EQ` `=` - Equality comparison
- `LT` `<` - Less than
- `GT` `>` - Greater than
- `LE` `<=` - Less than or equal
- `GE` `>=` - Greater than or equal
- `NE` `<>` - Not equal
- `DOTDOT` `..` - Range operator

### Delimiters

- `LPAREN` `(` - Left parenthesis
- `RPAREN` `)` - Right parenthesis
- `LBRACKET` `[` - Left bracket
- `RBRACKET` `]` - Right bracket
- `SEMICOLON` `;` - Statement separator
- `COMMA` `,` - Comma separator
- `COLON` `:` - Type separator
- `DOT` `.` - Statement/program terminator

### Literals

- `ID(name)` - Identifier (variable/program name)
- `INTEGER(value)` - Integer literal
- `REAL(value)` - Real (floating-point) literal
- `UNKNOWN(char)` - Unknown character

## Lexer Features

- **Whitespace Handling**: Ignores spaces, tabs, and line breaks
- **Comment Removal**: Strips Pascal-style curly brace comments `{ ... }`
- **Case Insensitivity**: Keywords are case-insensitive (PROGRAM, program, Program all recognized)
- **Number Recognition**: Distinguishes between integers and real numbers
- **Error Handling**: Reports unknown characters as UNKNOWN tokens

## Files in This Lab

- `lexer.l` - Flex specification file defining tokens and rules
- `sample1.pas` - Simple Pascal program example
- `sample2.pas` - Pascal program with arithmetic example
