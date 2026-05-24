from enum import IntEnum

TABLE_SIZE = 211


class Kind(IntEnum):
    VAR = 0
    CONST = 1
    FUNC = 2
    ARRAY = 3
    PROC = 4
    PARAM = 5


class Type(IntEnum):
    INT = 0
    REAL = 1
    VOID = 2
    BOOL = 3
    CHAR = 4


KIND_NAMES = {
    Kind.VAR: "variable",
    Kind.CONST: "constant",
    Kind.FUNC: "function",
    Kind.ARRAY: "array",
    Kind.PROC: "procedure",
    Kind.PARAM: "parameter",
}
TYPE_NAMES = {
    Type.INT: "integer",
    Type.REAL: "real",
    Type.VOID: "void",
    Type.BOOL: "bool",
    Type.CHAR: "char",
}


def hash_function(key):
    h = 5381
    for c in key:
        h = ((h << 5) + h) + ord(c)
    return h % TABLE_SIZE


class SymbolTableEntry:
    __slots__ = ("name", "kind", "type", "scope_level", "line", "next")

    def __init__(self, name, kind, typ, scope_level, line):
        self.name = name
        self.kind = kind
        self.type = typ
        self.scope_level = scope_level
        self.line = line
        self.next = None


class SymbolTable:
    def __init__(self, scope_level=0, parent=None):
        self.slots = [None] * TABLE_SIZE
        self.scope_level = scope_level
        self.parent = parent

    def _hash(self, name):
        return hash_function(name)

    def lookup_current(self, name):
        idx = self._hash(name)
        entry = self.slots[idx]
        while entry:
            if entry.name == name:
                return entry
            entry = entry.next
        return None

    def lookup(self, name):
        entry = self.lookup_current(name)
        if entry:
            return entry
        if self.parent:
            return self.parent.lookup(name)
        return None

    def insert(self, name, kind, typ, line):
        if self.lookup_current(name):
            return False
        idx = self._hash(name)
        entry = SymbolTableEntry(name, kind, typ, self.scope_level, line)
        entry.next = self.slots[idx]
        self.slots[idx] = entry
        return True

    def delete(self, name):
        idx = self._hash(name)
        entry = self.slots[idx]
        prev = None
        while entry:
            if entry.name == name:
                if prev:
                    prev.next = entry.next
                else:
                    self.slots[idx] = entry.next
                return True
            prev = entry
            entry = entry.next
        return False

    def print(self):
        from rich.console import Console
        from rich.table import Table

        console = Console()
        table = Table(title=f"Symbol Table (scope level {self.scope_level})")
        table.add_column("Index", justify="right")
        table.add_column("Name")
        table.add_column("Kind")
        table.add_column("Type")
        table.add_column("Scope", justify="right")
        table.add_column("Line", justify="right")
        count = 0
        for i in range(TABLE_SIZE):
            entry = self.slots[i]
            while entry:
                kind_str = KIND_NAMES.get(entry.kind, str(entry.kind))
                type_str = TYPE_NAMES.get(entry.type, str(entry.type))
                table.add_row(
                    str(i),
                    entry.name,
                    kind_str,
                    type_str,
                    str(entry.scope_level),
                    str(entry.line),
                )
                count += 1
                entry = entry.next
        console.print(table)
        console.print(f"Total entries: {count}\n")


def begin_scope(current):
    new_table = SymbolTable(scope_level=current.scope_level + 1, parent=current)
    return new_table


def end_scope(current):
    current.print()
    return current.parent
