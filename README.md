# Eigene Mini-Programmiersprache – Übersicht & Befehle

Dieses Projekt ist ein vollständiger Compiler-Workflow für eine kleine, eigene Sprache, die in Python geschrieben ist und nach x64-Assembler übersetzt wird.

## Projektüberblick

- **Lexer:** Zerlegt Quelltext in Tokens.
- **Parser:** Baut aus Tokens einen Abstract Syntax Tree (AST).
- **Codegen:** Übersetzt den AST in NASM-Assembler.
- **Build:** Erstellt aus dem Assembler-Code eine ausführbare Datei.
- **main.py:** Steuert den gesamten Ablauf.

## Projektstruktur

- **main.py** – Einstiegspunkt, steuert den Ablauf.
- **lexer.py** – Wandelt Quelltext in Tokens um.
- **parser.py** – Erstellt den AST aus Tokens.
- **ast_nodes.py** – Definiert die AST-Knoten (Program, CallStatement, Identifier, NumberLiteral, StringLiteral, ForNode, IfNode, BinaryOp).
- **codegen_asm.py** – Übersetzt AST in NASM-Assembler.
- **build.py** – Baut und startet das Programm.
- **output/** – Enthält generierten Assembler- und Maschinencode.
- **docs/** – Dokumentation und Erklärungen.

## Sprachbefehle

Folgende Befehle sind aktuell in der Sprache möglich:

- `log([<string|number|varname>, ...]);`  
  Gibt Werte auf der Konsole aus (über printf).

- `iniv([<varname>, ...]);`  
  Initialisiert Variablen.

- `defv([<varname>, <value>, ...]);`  
  Weist Variablen Werte zu.

- `getForCounter();`  
  Gibt den aktuellen Zählerwert in einer For-Schleife zurück (nur innerhalb von `for` verwendbar).

- `for(<number>){ ... };`  
  Führt den Block <number> mal aus. Innerhalb des Blocks kann mit `getForCounter()` auf den aktuellen Schleifenzähler zugegriffen werden.

- `if(<condition>){ ... };`  
  Führt den Block aus, wenn die Bedingung erfüllt ist. Bedingungen können z.B. `==`, `!=`, `<=`, `>=` verwenden.

- `getInput(<message>);`  
  Liest eine Zahl von der Konsole ein und gibt sie zurück.

## Beispiel

```plaintext
iniv(x, y);
defv(x, "Hello", y, "");
for(5){
    defv(x, getForCounter());
    log(x);
    if(x == 2){
        for(3){
            defv(y, getForCounter());
            log(y);
        };
    };
};
```

## Wie funktioniert der Compiler?

1. **Quelltext schreiben** (z.B. in `source.lang`)
2. **main.py ausführen**  
   → Lexer, Parser, Codegen, Build laufen automatisch ab  
   → Ergebnis: Ausführbare Datei im `output/`-Ordner

## Weiterführende Dokumentation

- Siehe Ordner `docs/` für detaillierte Erklärungen zu Parser, Codegen und Architektur.
