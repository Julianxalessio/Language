from dataclasses import dataclass
from turtle import left, right
from typing import List

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
    counter: object  # NumberLiteral oder Identifier
    body: list

@dataclass
class IfNode:
    condition: object
    body: list

@dataclass
class BinaryOp:
    left: object
    op: str
    right: object

class InputNode:
    pass