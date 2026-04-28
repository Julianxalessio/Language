from lexer import Lexer
from parser import Parser
from codegen_asm import compile_program
from build import build, execute
import sys


def compile_source(source: str):
    tokens = Lexer(source).tokenize()
    ast = Parser(tokens).parse()
    #print(ast)
    return compile_program(ast)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1].endswith(".lang"):
            with open(sys.argv[1], "r", encoding="utf-8") as f:
                source = f.read()
        else:
            print("Error: Input file must have a .lang extension.")
            sys.exit(1)
    else:
        print("Error: Please provide a .lang file as an argument.")
        sys.exit(1)
    #with open("source.lang", "r", encoding="utf-8") as f:
    #    source = f.read()
    asm_source = compile_source(source)
    exe_path = build(asm_source)
    execute(exe_path)