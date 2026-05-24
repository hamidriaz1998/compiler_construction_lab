# Transformed CFG for a Subset of Pascal

The original grammar (`subset_pascal_cfg.md`) is **LALR(1)** but not suitable for **recursive-descent / LL(1)** parsing because it contains:

- **Left recursion** in several productions (e.g. `identifier_list`, `declarations`, `statement_list`, `simple_expression`, `term`, …).
- **Common left-prefixes** that require **left factoring** (e.g. `variable` vs `procedure_statement` both starting with `id`, `expression → simple_expression … | simple_expression relop …`, `factor → id | id ( expression_list )`).

This document rewrites the grammar after applying:

1. **Elimination of immediate left recursion** using the standard transformation
   `A → A α | β   ⟹   A → β A'     A' → α A' | ε`
2. **Left factoring** using
   `A → α β₁ | α β₂   ⟹   A → α A'     A' → β₁ | β₂`

`ε` denotes the empty string. Primed non-terminals (e.g. `identifier_list'`) are newly introduced by the transformations.

---

## 1. Summary of Changes

| # | Non-terminal | Problem | Transformation |
|---|---|---|---|
| 1 | `identifier_list` | left recursion | eliminated → `identifier_list'` |
| 2 | `declarations` | left recursion (β = ε) | eliminated → `declarations'` |
| 3 | `subprogram_declarations` | left recursion (β = ε) | eliminated → `subprogram_declarations'` |
| 4 | `parameter_list` | left recursion | eliminated → `parameter_list'` |
| 5 | `statement_list` | left recursion | eliminated → `statement_list'` |
| 6 | `statement` | common prefix `id` (via `variable` and `procedure_statement`) | left-factored → `statement_tail` |
| 7 | `variable` | common prefix `id` | left-factored → `variable'` |
| 8 | `procedure_statement` | common prefix `id` | left-factored → `procedure_statement'` |
| 9 | `expression_list` | left recursion | eliminated → `expression_list'` |
| 10 | `expression` | common prefix `simple_expression` | left-factored → `expression'` |
| 11 | `simple_expression` | left recursion | eliminated → `simple_expression'` |
| 12 | `term` | left recursion | eliminated → `term'` |
| 13 | `factor` | common prefix `id` | left-factored → `factor'` |

Unchanged productions: `program`, `type`, `standard_type`, `subprogram_declaration`, `subprogram_head`, `arguments`, `compound_statement`, `optional_statements`, `sign`.

---

## 2. Transformed Grammar

### Program structure (unchanged)

```
program  →  program id ( identifier_list ) ;
            declarations
            subprogram_declarations
            compound_statement
```

### Identifier list — left recursion eliminated

```
identifier_list   →  id identifier_list'
identifier_list'  →  , id identifier_list'
                  |  ε
```

### Declarations — left recursion eliminated (with β = ε)

```
declarations   →  declarations'
declarations'  →  var identifier_list : type ; declarations'
               |  ε
```

### Type (unchanged — no common prefix)

```
type  →  standard_type
      |  array [ num .. num ] of standard_type
```

### Standard type (unchanged)

```
standard_type  →  integer
               |  real
```

### Subprogram declarations — left recursion eliminated (with β = ε)

```
subprogram_declarations   →  subprogram_declarations'
subprogram_declarations'  →  subprogram_declaration ; subprogram_declarations'
                          |  ε
```

### Subprogram declaration (unchanged)

```
subprogram_declaration  →  subprogram_head declarations compound_statement
```

### Subprogram head (unchanged — distinct first tokens)

```
subprogram_head  →  function  id arguments : standard_type ;
                 |  procedure id arguments ;
```

### Arguments (unchanged)

```
arguments  →  ( parameter_list )
           |  ε
```

### Parameter list — left recursion eliminated

```
parameter_list   →  identifier_list : type parameter_list'
parameter_list'  →  ; identifier_list : type parameter_list'
                 |  ε
```

### Compound statement (unchanged)

```
compound_statement  →  begin
                       optional_statements
                       end
```

### Optional statements (unchanged)

```
optional_statements  →  statement_list
                     |  ε
```

### Statement list — left recursion eliminated

```
statement_list   →  statement statement_list'
statement_list'  →  ; statement statement_list'
                 |  ε
```

### Statement — left factored on the common prefix `id`

Originally, both `variable assignop expression` and `procedure_statement` can begin with `id`. Substituting the right-hand sides of `variable` and `procedure_statement` and factoring the common `id` gives:

```
statement      →  id statement_tail
               |  compound_statement
               |  if expression then statement else statement
               |  while expression do statement

statement_tail →  assignop expression                   (was: id assignop expression)
               |  [ expression ] assignop expression    (was: id [ expression ] assignop expression)
               |  ( expression_list )                   (was: id ( expression_list ))
               |  ε                                     (was: id  — parameterless procedure call)
```

### Variable — left factored (kept for completeness if still referenced)

```
variable   →  id variable'
variable'  →  [ expression ]
           |  ε
```

### Procedure statement — left factored (kept for completeness if still referenced)

```
procedure_statement   →  id procedure_statement'
procedure_statement'  →  ( expression_list )
                      |  ε
```

> **Note:** After the `statement` non-terminal is left-factored as above, `variable` and `procedure_statement` are no longer strictly required — they are subsumed by `statement_tail`. They are shown here so downstream rules that referenced them can still be resolved.

### Expression list — left recursion eliminated

```
expression_list   →  expression expression_list'
expression_list'  →  , expression expression_list'
                  |  ε
```

### Expression — left factored on `simple_expression`

```
expression   →  simple_expression expression'
expression'  →  relop simple_expression
             |  ε
```

### Simple expression — left recursion eliminated

Original had two non-recursive alternatives (`term`, `sign term`) and one recursive (`simple_expression addop term`). The transformation yields:

```
simple_expression   →  term simple_expression'
                    |  sign term simple_expression'
simple_expression'  →  addop term simple_expression'
                    |  ε
```

### Term — left recursion eliminated

```
term   →  factor term'
term'  →  mulop factor term'
       |  ε
```

### Factor — left factored on `id`

```
factor   →  id factor'
         |  num
         |  ( expression )
         |  not factor
factor'  →  ( expression_list )
         |  ε
```

### Sign (unchanged)

```
sign  →  +
      |  -
```

---

## 3. Full Transformed Grammar at a Glance

```
program                  →  program id ( identifier_list ) ;
                            declarations subprogram_declarations compound_statement

identifier_list          →  id identifier_list'
identifier_list'         →  , id identifier_list' | ε

declarations             →  declarations'
declarations'            →  var identifier_list : type ; declarations' | ε

type                     →  standard_type
                         |  array [ num .. num ] of standard_type

standard_type            →  integer | real

subprogram_declarations  →  subprogram_declarations'
subprogram_declarations' →  subprogram_declaration ; subprogram_declarations' | ε

subprogram_declaration   →  subprogram_head declarations compound_statement

subprogram_head          →  function  id arguments : standard_type ;
                         |  procedure id arguments ;

arguments                →  ( parameter_list ) | ε

parameter_list           →  identifier_list : type parameter_list'
parameter_list'          →  ; identifier_list : type parameter_list' | ε

compound_statement       →  begin optional_statements end

optional_statements      →  statement_list | ε

statement_list           →  statement statement_list'
statement_list'          →  ; statement statement_list' | ε

statement                →  id statement_tail
                         |  compound_statement
                         |  if expression then statement else statement
                         |  while expression do statement

statement_tail           →  assignop expression
                         |  [ expression ] assignop expression
                         |  ( expression_list )
                         |  ε

variable                 →  id variable'
variable'                →  [ expression ] | ε

procedure_statement      →  id procedure_statement'
procedure_statement'     →  ( expression_list ) | ε

expression_list          →  expression expression_list'
expression_list'         →  , expression expression_list' | ε

expression               →  simple_expression expression'
expression'              →  relop simple_expression | ε

simple_expression        →  term simple_expression'
                         |  sign term simple_expression'
simple_expression'       →  addop term simple_expression' | ε

term                     →  factor term'
term'                    →  mulop factor term' | ε

factor                   →  id factor'
                         |  num
                         |  ( expression )
                         |  not factor
factor'                  →  ( expression_list ) | ε

sign                     →  + | -
```

---

## 4. Notes on the Transformation

- **No indirect left recursion.** Each recursive non-terminal in the original grammar references *itself* directly, so the general Paull's algorithm is not required — the single-step rule for immediate left recursion suffices.
- **Dangling-else.** The ambiguity from `statement → if expression then statement [else statement]` is not fixed by the above transformations; it must still be resolved by a disambiguation rule (prefer shift, i.e. bind `else` to the nearest unmatched `then`).
- **Lexical conventions (Section A.4)** and the **reserved-keyword list** are unchanged and still apply verbatim from the original document.
