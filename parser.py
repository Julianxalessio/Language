from ast_nodes import ForNode, Program, CallStatement, Identifier, NumberLiteral, StringLiteral

"""
PARSER-TEMPLATE

Aktuelle Minimal-Grammatik:

    program  := statement* EOF
    statement := call_stmt
    call_stmt := IDENT LPAREN args? RPAREN SEMICOLON
    args      := literal_or_ident (COMMA literal_or_ident)*
    literal_or_ident := STRING | NUMBER | IDENT

Regel:
- Es muss mindestens ein Statement geben.

Erweiterungspunkte:
- weitere Statement-Typen (let, if, while, fn)
- Ausdrucksparser mit Operator-Prioritaet
"""


class Parser:
    """Wandelt Token-Liste in ein Programm-Template-AST um."""

    def __init__(self, tokens):
        self.tokens = tokens
        self.index = 0

    def current(self):
        """Gibt das aktuelle Token an self.index zurueck."""
        return self.tokens[self.index]

    def consume(self, kind):
        """Verbraucht genau ein Token des erwarteten Typs oder wirft SyntaxError."""
        token = self.current()
        if token.kind != kind:
            raise SyntaxError(
                f"Erwartet {kind}, gefunden {token.kind} an Position {token.pos}"
            )
        self.index += 1
        return token

    def parse(self):
        statements = []
        while self.current().kind != "EOF":
            stmt = self.parse_statement()
            if stmt is not None:
                statements.append(stmt)

        self.consume("EOF")
        if not statements:
            raise SyntaxError("Leeres Programm.")

        return Program(statements)


    def parse_for_statement(self):
        self.consume("FOR")
        self.consume("LPAREN")
        count = self.consume("NUMBER").value
        self.consume("RPAREN")
        self.consume("LBRACE")
        body = self.parse_block()
        return ForNode(count, body)

    def parse_block(self):
        statements = []
        while self.current().kind != "RBRACE":
            statements.append(self.parse_statement())
        self.consume("RBRACE")
        return statements

    def parse_call_statement(self):
        function_name = self.consume("IDENT").value
        self.consume("LPAREN")

        args = []
        if self.current().kind != "RPAREN":
            args.append(self.parse_argument())
            while self.current().kind == "COMMA":
                self.consume("COMMA")
                args.append(self.parse_argument())

        self.consume("RPAREN")
        self.consume("SEMICOLON")
        return CallStatement(function_name, args)

    def parse_argument(self):
        token = self.current()

        if token.kind == "STRING":
            self.index += 1
            return StringLiteral(token.value)

        if token.kind == "NUMBER":
            self.index += 1
            return NumberLiteral(int(token.value))

        # Funktionsaufruf als Argument: IDENT LPAREN ... RPAREN
        if token.kind == "IDENT":
            # Prüfe, ob es ein Funktionsaufruf ist
            if self.index + 1 < len(self.tokens) and self.tokens[self.index + 1].kind == "LPAREN":
                function_name = self.consume("IDENT").value
                self.consume("LPAREN")
                args = []
                if self.current().kind != "RPAREN":
                    args.append(self.parse_argument())
                    while self.current().kind == "COMMA":
                        self.consume("COMMA")
                        args.append(self.parse_argument())
                self.consume("RPAREN")
                return CallStatement(function_name, args)
            else:
                self.index += 1
                return Identifier(token.value)

        raise SyntaxError(f"Unerwartetes Argument-Token {token.kind} an Position {token.pos}")

    def parse_statement(self):
        # Überspringe überflüssige Semikolons, aber nicht am Dateiende
        while self.current().kind == "SEMICOLON":
            self.consume("SEMICOLON")
            if self.current().kind == "EOF":
                return None
        if self.current().kind == "IDENT":
            return self.parse_call_statement()
        if self.current().kind == "FOR":
            return self.parse_for_statement()
        if self.current().kind == "EOF":
            return None
        raise SyntaxError(f"Unerwartetes Statement-Token {self.current().kind} an Position {self.current().pos}")
