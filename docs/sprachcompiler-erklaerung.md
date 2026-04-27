# Mini-Sprache in Python und ASM - Verstaendliche Erklaerung

Diese Datei erklaert dir Schritt fuer Schritt, wie dein Projekt funktioniert und wie daraus eine echte Programmiersprache wachsen kann.

## 1) Was du gerade gebaut hast

Du hast einen kleinen Compiler gebaut:

1. Er nimmt einen Ausdruck als Text, z. B. `1 + 2 * 3`.
2. Er zerlegt den Text in Tokens (Lexer).
3. Er baut daraus eine Baumstruktur (Parser + AST).
4. Er erzeugt daraus Assembler-Code (Codegen).
5. Er baut den Assembler-Code mit `nasm` + `gcc` zu einer `.exe`.
6. Die `.exe` liefert das Ergebnis als Exit-Code.

Das ist bereits ein echter Compiler-Workflow in klein.

## 2) Projektstruktur und Aufgabe jeder Datei

- `main.py`
  Startpunkt. Steuert den ganzen Ablauf: Source -> Lexer -> Parser -> Codegen -> Build -> Run.

- `lexer.py`
  Wandelt Text in Tokens um, z. B. Zahl, `+`, `-`, `*`, `(`, `)`.

- `parser.py`
  Liest die Tokens und baut einen AST (Abstract Syntax Tree), also eine strukturierte Darstellung der Rechnung.

- `ast_nodes.py`
  Definiert die AST-Knoten, z. B. `Number` und `BinaryOp`.

- `codegen_asm.py`
  Uebersetzt den AST in NASM-Assembler.

- `build.py`
  Baut und startet das Programm.
  Aktuell wird in den Ordner `output/` geschrieben:
  - `output/output.asm`
  - `output/output.obj`
  - `output/output.exe`

## 3) Warum nicht alles direkt in ASM schreiben?

Direkt ASM zu schreiben geht, ist aber fuer eine Programmiersprache unpraktisch.

Besser ist dieser Weg:

1. Sprache als Text (benutzerfreundlich)
2. Compiler verarbeitet den Text
3. Compiler erzeugt ASM/Maschinencode

So kannst du spaeter sehr einfach neue Sprachfeatures hinzufuegen (Variablen, if, while, Funktionen), ohne alles im ASM per Hand zu pflegen.

## 4) Was ist der AST und warum ist er wichtig?

Beispiel: `1 + 2 * 3`

Der Parser baut nicht einfach links-nach-rechts, sondern mit Operator-Prioritaet:

- zuerst `2 * 3`
- dann `1 + (2 * 3)`

Als Baum:

- `+`
- links: `1`
- rechts: `*`
  - links: `2`
  - rechts: `3`

Genau diesen Baum nutzt der Codegenerator, um korrekten ASM-Code zu erzeugen.

## 5) Warum kam vorher der WinMain-Fehler?

Du hattest zuerst Linux-artigen Entry-Point (`_start` + `syscall`) erzeugt.
Unter Windows mit MinGW/GCC erwartet der Linker standardmaessig `main`.

Jetzt ist es korrekt:

- ASM exportiert `main`
- `main` gibt mit `ret` zurueck
- Rueckgabewert in `rax` wird zum Prozess-Exit-Code

## 6) Warum sieht man das Ergebnis als Exit-Code?

Deine erzeugte `.exe` druckt noch nichts auf die Konsole.
Sie beendet sich nur mit einem Rueckgabewert.

Bei `1 + 2 * 3` ist das Ergebnis `7`, daher Exit-Code `7`.

Hinweis: Exit-Codes sind praktisch auf 0 bis 255 begrenzt. Fuer groessere Zahlen oder normale Ausgabe solltest du spaeter `print`/`printf` einbauen.

## 7) Wie du daraus eine richtige Sprache machst

Empfohlene Reihenfolge:

1. Datei-Eingabe statt festem String
   - z. B. `python main.py beispiel.lang`

2. Variablen
   - `let x = 5`
   - `x * 3`

3. Statements
   - mehrere Zeilen und Zuweisungen

4. Ausgabe
   - z. B. eingebautes `print(...)`

5. Kontrollfluss
   - `if`, `while`

6. Funktionen
   - `fn add(a, b) { ... }`

7. Typen/Semantik-Checks
   - sinnvolle Fehlermeldungen mit Zeile/Spalte

## 8) Mini-Merkbild fuer den Ablauf

Source-Code
-> Lexer (Tokens)
-> Parser (AST)
-> Codegen (ASM)
-> Assembler/Linker (EXE)
-> Ausfuehren

## 9) Nächster sinnvoller Schritt in deinem Projekt

Wenn du lernst, ist der beste naechste Schritt:

1. Source aus einer `.lang` Datei lesen
2. Token-Liste und AST optional debug-ausgeben
3. Danach Variablen einfuehren

So siehst du in jeder Stufe genau, was dein Compiler macht.
