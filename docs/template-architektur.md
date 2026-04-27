# Sprach-Template Architektur

Dieses Projekt ist jetzt bewusst ein Grundgeruest.

## Startregel

- Das erste Statement muss `log(...)` sein.
- `log(...)` arbeitet wie `print(...)`.

## Pipeline

1. `lexer.py`: Text -> Tokens
2. `parser.py`: Tokens -> AST
3. `codegen_asm.py`: AST -> kompiliertes Programmobjekt (Template)
4. `build.py`: Build-Hook (Template)
5. `build.py`: Execute-Hook (Runtime)

## Was bereits funktioniert

- Funktionsaufrufe als Statements: `name(arg1, arg2);`
- Built-in Funktion: `log(...)`
- Argumente: String, Zahl, Identifier

## Erweiterungspunkte

- `ast_nodes.py`
  - Neue Knoten definieren (z. B. LetStatement, IfStatement, WhileStatement)

- `lexer.py`
  - Neue Tokens fuer Operatoren und Keywords

- `parser.py`
  - Neue Grammatik-Regeln fuer Statements und Ausdruecke

- `codegen_asm.py`
  - Semantikcheck
  - Optional wieder echter ASM/Bytecode-Codegen

- `build.py`
  - Richtiger Build-Prozess je nach Backend

## Beispiel

`source.lang`:

log("Hallo Welt");
log(123, "ok");

Ausgabe:

Hallo Welt
123 ok
