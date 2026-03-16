# Lab 3: Lexical Analysis Implementation
## Comparison of Lexical Analyzer Approaches

In this lab, I have implemented three approaches to lexical analysis for a subset of the Pascal language: a state-based lexer, a stateless modular lexer, and a transition-table lexer. All three recognize the same tokens but differ in how the scanning logic is organized. Double buffer parsing based `BufferManager` is used from lab3.

### State-Based Lexer

The state-based lexer directly implements a deterministic finite automaton (DFA) using a state variable and conditional transitions. Each state corresponds to a stage in token recognition (e.g., identifier, integer, real number).

**Pros**

* Closely reflects the theoretical DFA model.
* Easy to understand for small languages.
* Debugging transitions is straightforward because the logic is explicit.

**Cons**

* Large conditional blocks as the number of tokens increases.
* Harder to maintain when new tokens or rules are added.
* Poor scalability for larger languages.

### Stateless (Modular) Lexer

The stateless approach separates token recognition into specialized functions such as `scan_identifier`, `scan_number`, and `scan_operator`. The main lexer decides which function to call based on the first character.

**Pros**

* Clean modular structure.
* Easier to read and maintain.
* Extending the lexer usually requires adding a new scanning function.

**Cons**

* Less directly connected to the DFA model.
* Some duplicated character-handling logic across functions.

### Transition-Table Lexer

The transition-table lexer represents the DFA using a table where rows represent states and columns represent character classes. State transitions are determined using `next_state = table[state][char_class]`. Accepting states determine which token should be returned.

**Pros**

* Very close to the formal DFA representation.
* Easy to modify by updating the table.
* Scales well to larger languages.

**Cons**

* Harder to understand initially.
* Requires an additional character classification step.

### Conclusion

The state-based approach is useful for understanding the mechanics of lexical analysis. The stateless modular approach provides the best readability and maintainability for hand-written lexers. The transition-table approach most closely matches formal compiler theory and is commonly used in automatically generated scanners.