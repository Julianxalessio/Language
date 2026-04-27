from ast_nodes import Program, CallStatement, Identifier, NumberLiteral, StringLiteral


def _escape_nasm_string(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def compile_program(ast_root):
    """Erzeugt NASM x64 Assembly fuer iniv/defv/log und nutzt printf zur Ausgabe."""
    if not isinstance(ast_root, Program):
        raise ValueError("Program-Root erwartet")

    data_lines = []
    text_lines = []

    data_lines.append('fmt_str db "%s", 0')
    data_lines.append('fmt_int db "%d", 0')
    data_lines.append('space_str db " ", 0')
    data_lines.append('nl_str db 10, 0')
    data_lines.append('nil_str db "<nil>", 0')

    string_labels = {}
    variables = {}
    string_counter = 0

    def string_label(value: str) -> str:
        nonlocal string_counter
        if value in string_labels:
            return string_labels[value]
        label = f"str_{string_counter}"
        string_counter += 1
        string_labels[value] = label
        escaped = _escape_nasm_string(value)
        data_lines.append(f'{label} db "{escaped}", 0')
        return label

    def ensure_variable(name: str):
        if name not in variables:
            variables[name] = f"var_{name}"
            data_lines.append(f"{variables[name]} dq nil_str")

    def arg_pointer_operand(arg):
        if isinstance(arg, StringLiteral):
            return f"{string_label(arg.value)}", False

        if isinstance(arg, NumberLiteral):
            return f"{string_label(str(arg.value))}", False

        if isinstance(arg, Identifier):
            if arg.name not in variables:
                raise ValueError(f"Unbekannter Bezeichner: {arg.name}")
            return variables[arg.name], True

        # Spezialfall: Marker für getForCounter()
        if arg == "__FOR_COUNTER__":
            # Rückgabe: aktueller Wert von i liegt auf [rsp], kein Label nötig
            return "[rsp]", True

        raise ValueError(f"Unbekanntes Argument: {type(arg).__name__ if not isinstance(arg, str) else arg}")

    def emit_printf_from_ptr(ptr_operand: str, is_memory_ptr: bool):
        text_lines.append("    sub rsp, 40")
        # Wenn der Pointer [rsp] ist, dann ist es ein Integer (getForCounter)
        if ptr_operand == "[rsp]":
            text_lines.append("    lea rcx, [rel fmt_int]")
            text_lines.append(f"    mov rdx, {ptr_operand}")
        else:
            text_lines.append("    lea rcx, [rel fmt_str]")
            if is_memory_ptr:
                text_lines.append(f"    mov rdx, [rel {ptr_operand}]")
            else:
                text_lines.append(f"    lea rdx, [rel {ptr_operand}]")
        text_lines.append("    call printf")
        text_lines.append("    add rsp, 40")

    def emit_log_call(args):
        for idx, arg in enumerate(args):
            ptr_operand, is_memory_ptr = arg_pointer_operand(arg)
            emit_printf_from_ptr(ptr_operand, is_memory_ptr)

            if idx < len(args) - 1:
                emit_printf_from_ptr("space_str", False)

        emit_printf_from_ptr("nl_str", False)


    for stmt in ast_root.statements:
        if isinstance(stmt, CallStatement):
            if stmt.function_name == "iniv":
                for arg in stmt.args:
                    if not isinstance(arg, Identifier):
                        raise ValueError("iniv(...) erwartet nur Variablennamen")
                    ensure_variable(arg.name)
                continue

            if stmt.function_name == "defv":
                if len(stmt.args) % 2 != 0:
                    raise ValueError("defv(...) erwartet Paare: varname, value")

                i = 0
                while i < len(stmt.args):
                    name_arg = stmt.args[i]
                    value_arg = stmt.args[i + 1]

                    if not isinstance(name_arg, Identifier):
                        raise ValueError("defv(...) erwartet als erstes Element im Paar einen Variablennamen")

                    ensure_variable(name_arg.name)
                    ptr_operand, is_memory_ptr = arg_pointer_operand(value_arg)

                    if is_memory_ptr:
                        text_lines.append(f"    mov rax, [rel {ptr_operand}]")
                    else:
                        text_lines.append(f"    lea rax, [rel {ptr_operand}]")
                    text_lines.append(f"    mov [rel {variables[name_arg.name]}], rax")

                    i += 2
                continue

            if stmt.function_name == "log":
                emit_log_call(stmt.args)
                continue

            raise ValueError(f"Unbekannte Funktion: {stmt.function_name}")

        elif type(stmt).__name__ == "ForNode":
            count = stmt.counter
            block_statements = stmt.body

            for_counter = len([l for l in text_lines if l.startswith('for_start_')])
            limit_var = f"var_for_limit_{for_counter}"
            data_lines.append(f"{limit_var} dq {count}")

            text_lines.append(f"    sub rsp, 8                 ; var_i reservieren")
            text_lines.append(f"    mov qword [rsp], 0         ; var_i = 0")
            text_lines.append(f"for_start_{for_counter}:")
            text_lines.append(f"    mov rax, [rsp]")
            text_lines.append(f"    cmp rax, [rel {limit_var}]")
            text_lines.append(f"    jge for_end_{for_counter}")


            # Erweiterung: Erlaube defv und getForCounter() im for-Block
            for block_stmt in block_statements:
                if not isinstance(block_stmt, CallStatement):
                    raise ValueError(f"Unbekanntes Statement im for-Block: {type(block_stmt).__name__}")

                # Ersetze getForCounter() durch aktuellen i-Wert (liegt auf [rsp])
                def replace_getForCounter(args):
                    new_args = []
                    for arg in args:
                        if isinstance(arg, CallStatement) and arg.function_name == "getForCounter" and len(arg.args) == 0:
                            # Erzeuge einen speziellen Marker für den i-Wert
                            new_args.append("__FOR_COUNTER__")
                        else:
                            new_args.append(arg)
                    return new_args

                if block_stmt.function_name == "log":
                    emit_log_call(replace_getForCounter(block_stmt.args))
                elif block_stmt.function_name == "defv":
                    # defv(varname, value)
                    args = replace_getForCounter(block_stmt.args)
                    if len(args) % 2 != 0:
                        raise ValueError("defv(...) erwartet Paare: varname, value")
                    i = 0
                    while i < len(args):
                        name_arg = args[i]
                        value_arg = args[i + 1]
                        if not isinstance(name_arg, Identifier):
                            raise ValueError("defv(...) erwartet als erstes Element im Paar einen Variablennamen")
                        ensure_variable(name_arg.name)
                        if value_arg == "__FOR_COUNTER__":
                            # Aktuellen i-Wert (liegt auf [rsp]) zuweisen
                            text_lines.append(f"    mov rax, [rsp]")
                            text_lines.append(f"    mov [rel {variables[name_arg.name]}], rax")
                        else:
                            ptr_operand, is_memory_ptr = arg_pointer_operand(value_arg)
                            if is_memory_ptr:
                                text_lines.append(f"    mov rax, [rel {ptr_operand}]")
                            else:
                                text_lines.append(f"    lea rax, [rel {ptr_operand}]")
                            text_lines.append(f"    mov [rel {variables[name_arg.name]}], rax")
                        i += 2
                else:
                    raise ValueError(f"Nur log(...) und defv(...) Aufrufe im for-Block erlaubt, gefunden: {block_stmt.function_name}")

            text_lines.append(f"    add qword [rsp], 1")
            text_lines.append(f"    jmp for_start_{for_counter}")
            text_lines.append(f"for_end_{for_counter}:")
            text_lines.append(f"    add rsp, 8")
            continue

        else:
            raise ValueError(f"Unbekanntes Statement: {type(stmt).__name__}")

    asm = []
    asm.append("default rel")
    asm.append("extern printf")
    asm.append("section .data")
    asm.extend(data_lines)
    asm.append("section .text")
    asm.append("global main")
    asm.append("main:")
    asm.extend(text_lines)
    asm.append("    xor eax, eax")
    asm.append("    ret")

    return "\n".join(asm)
