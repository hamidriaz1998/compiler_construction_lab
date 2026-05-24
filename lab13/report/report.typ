#import "lab-cover-template.typ": lab-cover

#lab-cover(
  lab-title: "Lab 13: Symbol Table Manager",
  logo: "./logo.png",
  session: "Session 2023 – 2027",
  student-name: "Hamid Riaz",
  student-id: "2023-CS-10",
  supervisor: "Mam Aliya Farooq",
  course: "CS-471L: Compiler Construction Lab",
  department: "Department of Computer Science",
  university: "University of Engineering and Technology",
  location: "Lahore, Pakistan",
)

#pagebreak()
#set list(indent: 1em)
#set enum(indent: 1em)
#set text(size: 12pt, font: "Times New Roman")
#show heading: set text(weight: "bold")
#show heading.where(level: 2): set text(size: 16pt)
#show heading.where(level: 3): set text(size: 14pt)

= Symbol Table Manager --- Test Report
<symbol-table-manager-test-report>
== Test Case 1: Valid Program (`tests/valid.pas`)
<test-case-1-valid-program-testsvalid.pas>
Full Subset Pascal program with variables, arrays, a function, and a
procedure.

#strong[Input:]

```pascal
program test(input, output);
var x, y : integer;
var arr : array [1 .. 10] of integer;

function max(a, b : integer) : integer;
var result : integer;
begin
    if a > b then
        result := a
    else
        result := b;
    max := result
end;

procedure print(n : integer);
begin
end;

begin
    x := 5;
    y := 10
end
```

#strong[Expected:] Parses successfully. Global scope (level 0) contains
`x`, `y`, `arr`, `max`, `print`. Function `max` scope (level 1) contains
`a`, `b`, `result`. Procedure `print` scope (level 1) contains `n`.

#strong[Actual:] Parsing successful. Output matches expectations
exactly.

#figure(
  align(center)[#table(
    columns: (32.43%, 36.49%, 31.08%),
    align: (auto, auto, auto),
    table.header([Scope 0 (global)], [Scope 1 (max)], [Scope 1 (print)]),
    table.hline(),
    [x --- variable --- integer],
    [a --- parameter --- integer],
    [n ---
      parameter --- integer],
    [y --- variable --- integer], [b --- parameter --- integer], [],
    [arr --- variable --- integer],
    [result --- variable ---
      integer],
    [],
    [max --- function --- integer], [], [],
    [print --- procedure --- void], [], [],
  )],
  kind: table,
)

#line(length: 100%)

== Test Case 2: Duplicate Declaration (`tests/duplicate.pas`)
<test-case-2-duplicate-declaration-testsduplicate.pas>
#strong[Input:]

```pascal
program test(input);
var x : integer;
var x : real;
begin
end
```

#strong[Expected:] Error on line 3 --- `x` is already declared in the
same scope as integer.

#strong[Actual:] `Error: Line 3: duplicate identifier 'x'`

#line(length: 100%)

== Test Case 3: Undeclared Identifier (`tests/undeclared.pas`)
<test-case-3-undeclared-identifier-testsundeclared.pas>
#strong[Input:]

```pascal
program test(input);
var
    x : integer;
begin
    y := 5
end
```

#strong[Expected:] Error on line 5 --- `y` was never declared.

#strong[Actual:] `Error: Line 5: undeclared identifier 'y'`

#line(length: 100%)

== Test Case 4: Nested Scope & Shadowing (`tests/nested_scope.pas`)
<test-case-4-nested-scope-shadowing-testsnested_scope.pas>
#strong[Input:]

```pascal
program test(input);
var x : integer;

procedure inner;
var x : real;
begin
end;

begin
end
```

#strong[Expected:] Parses successfully. Global scope has `x: integer`
and `inner: procedure`. The `inner` procedure's scope has `x: real`
(shadows the global `x`). The two `x` identifiers reside in different
scopes and do not conflict.

#strong[Actual:] Parsing successful. Global scope: `x (integer)`,
`inner (procedure)`. Inner scope: `x (real)`. Shadowing works correctly.

#line(length: 100%)

== Test Case 5: Parameter Shadowing (`tests/func_shadow.pas`)
<test-case-5-parameter-shadowing-testsfunc_shadow.pas>
#strong[Input:]

```pascal
program test(input);
var
    x : integer;

function foo(x : integer) : integer;
var
    y : integer;
begin
    y := x
end;

begin
    x := 5
end
```

#strong[Expected:] Parses successfully. Global `x` (integer) and `foo`
(function) in scope 0. Parameter `x` (integer) and local `y` (integer)
in scope 1. The `x` referenced inside `foo` resolves to the parameter
(scope 1), not the global variable.

#strong[Actual:] Parsing successful.

- Scope 0: `x (variable, integer)` and `foo (function, integer)`
- Scope 1: `x (parameter, integer)` and `y (variable, integer)` Lookup
  correctly finds the parameter `x` inside the function body.

#line(length: 100%)

== Limitations & Known Bugs
<limitations-known-bugs>
+ #strong[No support for nested function declarations.] The grammar does
  not allow functions to be declared inside other functions, so only two
  levels of scope nesting (global + function body) are possible.

+ #strong[Array type detail not recorded.] Array declarations store only
  the element type (integer/real), not the bounds or the fact that the
  variable is an array. A full implementation would track
  `array[1..10] of integer` as a distinct type with range information.

+ #strong[Function return type not propagated.] The function name is
  inserted into the symbol table with a placeholder type (`integer`)
  before the return type is parsed. A full implementation would update
  the entry after parsing the return type annotation.

+ #strong[No type checking.] The symbol table records types but the
  parser does not verify type compatibility in assignments, expressions,
  or function calls. Type errors (e.g., assigning a real to an integer
  variable) are not reported.
