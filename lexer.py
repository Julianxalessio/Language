from dataclasses import dataclass


@dataclass
class Token:
    kind: str
    value: str
    pos: int


class Lexer:
    """
    TEMPLATE-LEXER
    Unterstützt aktuell nur das Grundgeruest fuer Funktionsaufrufe wie:
        log("Hallo", 123);

    Erweiterungspunkte:
    - neue Operatoren (+, -, *, ...)
    - neue Keywords (let, if, while, fn, ...)
    - Kommentare
    """

    def __init__(self, source: str):
        self.source = source
        self.length = len(source)
        self.index = 0

    def tokenize(self):
        tokens = []
        while self.index < self.length:
            ch = self.source[self.index]

            if ch.isspace():
                self.index += 1
                continue

            if ch.isdigit():
                start = self.index
                while self.index < self.length and self.source[self.index].isdigit():
                    self.index += 1
                tokens.append(Token("NUMBER", self.source[start:self.index], start))
                continue


            two_char_ops = {
                "==": "EQ",
                "!=": "NEQ",
                "<=": "LTE",
                ">=": "GTE",
            }

            pair = self.source[self.index:self.index+2]
            if pair in two_char_ops:
                tokens.append(Token(two_char_ops[pair], pair, self.index))
                self.index += 2
                continue

            # Single-char arithmetic operators
            if ch == '+':
                tokens.append(Token("PLUS", ch, self.index))
                self.index += 1
                continue
            if ch == '-':
                tokens.append(Token("MINUS", ch, self.index))
                self.index += 1
                continue
            if ch == '*':
                tokens.append(Token("STAR", ch, self.index))
                self.index += 1
                continue
            if ch == '/':
                tokens.append(Token("SLASH", ch, self.index))
                self.index += 1
                continue

            if ch.isalpha() or ch == "_":
                start = self.index
                while self.index < self.length and (
                    self.source[self.index].isalnum() or self.source[self.index] == "_"
                ):
                    self.index += 1
                value = self.source[start:self.index]
                kind = "FOR" if value == "for" else "IF" if value == "if" else "IDENT"
                tokens.append(Token(kind, value, start))
                continue

            if ch == '"':
                start = self.index
                self.index += 1
                value_chars = []
                while self.index < self.length and self.source[self.index] != '"':
                    value_chars.append(self.source[self.index])
                    self.index += 1

                if self.index >= self.length:
                    raise SyntaxError(f"Nicht geschlossener String ab Position {start}")

                self.index += 1
                tokens.append(Token("STRING", "".join(value_chars), start))
                continue

            if ch == ";":
                tokens.append(Token("SEMICOLON", ch, self.index))
                self.index += 1
                continue

            if ch == ",":
                tokens.append(Token("COMMA", ch, self.index))
                self.index += 1
                continue

            if ch == "(":
                tokens.append(Token("LPAREN", ch, self.index))
                self.index += 1
                continue

            if ch == ")":
                tokens.append(Token("RPAREN", ch, self.index))
                self.index += 1
                continue

            if ch == '{':
                tokens.append(Token("LBRACE", "{", self.index))
                self.index += 1
                continue

            if ch == '}':
                tokens.append(Token("RBRACE", "}", self.index))
                self.index += 1
                continue

            raise SyntaxError(f"Unerwartetes Zeichen '{ch}' an Position {self.index}")

        tokens.append(Token("EOF", "", self.index))
        return tokens
