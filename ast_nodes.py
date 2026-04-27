from dataclasses import dataclass
from typing import List


# ===== AST TEMPLATE =====
# Diese Knoten sind absichtlich minimal gehalten.
# Hier kannst du spaeter eigene Sprach-Features ergaenzen.


@dataclass
class Program:
    statements: List[object]


@dataclass
class CallStatement:
    function_name: str
    args: List[object]

@dataclass
class Identifier:
    name: str


@dataclass
class NumberLiteral:
    value: int


@dataclass
class StringLiteral:
    value: str

@dataclass
class ForNode:
    counter: int
    body: list