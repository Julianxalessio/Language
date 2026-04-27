from lexer import Lexer
from parser import Parser
from codegen_asm import compile_program
from build import build, execute


def compile_source(source: str):
    tokens = Lexer(source).tokenize()
    ast = Parser(tokens).parse()
    print("AST:", ast)
    print()
    return compile_program(ast)


if __name__ == "__main__":
    with open("source.lang", "r", encoding="utf-8") as f:
        source = f.read()

    asm_source = compile_source(source)
    exe_path = build(asm_source)
    execute(exe_path)