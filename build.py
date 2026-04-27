import os
import subprocess


def build(compiled_program, asm_file="output/output.asm", obj_file="output/output.obj", exe_file="output/output.exe"):
    """Schreibt Assembly und baut daraus eine Windows-Exe mit NASM + GCC."""
    os.makedirs("output", exist_ok=True)

    with open(asm_file, "w", encoding="utf-8") as f:
        f.write(compiled_program)

    subprocess.run(["nasm", "-f", "win64", asm_file, "-o", obj_file], check=True)
    subprocess.run(["gcc", obj_file, "-o", exe_file, "-mconsole"], check=True)

    return exe_file


def execute(built_program):
    """Startet die gebaute Exe."""
    return subprocess.run([built_program], check=False)
