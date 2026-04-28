from ast_nodes import Program, CallStatement, Identifier, NumberLiteral, StringLiteral

def compile_program(ast_root):
    text_lines = []
    data_lines = []
    variables = {}
    var_types = {}  # name -> "int" | "str"
    current_for_counter = None
    temp_counter = 0

    # Format-Strings
    data_lines.append('fmt_int db "%d", 10, 0')
    data_lines.append('fmt_str db "%s", 10, 0')
    data_lines.append('fmt_in db "%s", 0')

    label_counter = {"if": 0, "for": 0}

    def new_label(prefix):
        label_counter[prefix] += 1
        return f"{prefix}_{label_counter[prefix]}"

    # -------------------------
    # Hilfsfunktionen
    # -------------------------

    def ensure_variable(name, vtype="int"):
        if name not in variables:
            label = f"var_{name}"
            variables[name] = label
            data_lines.append(f"{label} dq 0")
        var_types[name] = vtype

    def arg_pointer_operand(arg):
        nonlocal current_for_counter
        nonlocal temp_counter

        if isinstance(arg, NumberLiteral):
            label = f"num_{arg.value}"
            if label not in variables:
                data_lines.append(f"{label} dd {arg.value}")
                variables[label] = label
            # is_var=False, is_int=True
            return label, False, True

        elif isinstance(arg, StringLiteral):
            label = f"str_{temp_counter}"
            temp_counter += 1
            escaped = arg.value.replace("\\", "\\\\").replace('"', '\\"')
            data_lines.append(f'{label} db "{escaped}", 0')
            # is_var=False, is_int=False
            return label, False, False

        elif isinstance(arg, Identifier):
            vtype = var_types.get(arg.name, "int")
            ensure_variable(arg.name, vtype)
            # is_var=True, is_int depends on tracked type
            return variables[arg.name], True, vtype == "int"

        # Binary Expressions
        elif hasattr(arg, 'op') and hasattr(arg, 'left'):
            left_ptr, _, _ = arg_pointer_operand(arg.left)
            right_ptr, _, _ = arg_pointer_operand(arg.right)

            temp = f"tmp_{temp_counter}"
            temp_counter += 1
            variables[temp] = temp
            data_lines.append(f"{temp} dd 0")

            text_lines.append(f"    mov eax, [rel {left_ptr}]")

            if arg.op == "PLUS":
                text_lines.append(f"    add eax, [rel {right_ptr}]")
            elif arg.op == "MINUS":
                text_lines.append(f"    sub eax, [rel {right_ptr}]")
            elif arg.op == "STAR":
                text_lines.append(f"    imul eax, [rel {right_ptr}]")
            elif arg.op == "SLASH":
                text_lines.append("    cdq")
                text_lines.append(f"    idiv dword [rel {right_ptr}]")
            else:
                raise ValueError(f"Unbekannter Operator: {arg.op}")

            text_lines.append(f"    mov [rel {temp}], eax")
            # is_var=False, is_int=True
            return temp, False, True

        # Funktionsaufrufe
        elif isinstance(arg, CallStatement):

            if arg.function_name == "getForCounter":
                if current_for_counter is None:
                    raise ValueError("getForCounter außerhalb von for")
                return current_for_counter, False, True

            elif arg.function_name == "toInt":
                if len(arg.args) != 1:
                    raise ValueError("toInt erwartet genau 1 Argument")

                ptr, is_var, _ = arg_pointer_operand(arg.args[0])

                temp = f"tmp_{temp_counter}"
                temp_counter += 1
                variables[temp] = temp
                data_lines.append(f"{temp} dd 0")

                # Wenn is_var: Variable enthält Adresse -> mov; sonst Label = Adresse -> lea
                if is_var:
                    text_lines.append(f"    mov rcx, [rel {ptr}]")
                else:
                    text_lines.append(f"    lea rcx, [rel {ptr}]")
                text_lines.append("    sub rsp, 40")
                text_lines.append("    call atoi")
                text_lines.append("    add rsp, 40")
                text_lines.append(f"    mov [rel {temp}], eax")

                return temp, False, True

            elif arg.function_name == "getInput":
                if len(arg.args) != 1 or not isinstance(arg.args[0], StringLiteral):
                    raise ValueError("getInput braucht genau 1 String")

                msg = arg.args[0].value
                msg_label = f"msg_{len(data_lines)}"
                data_lines.append(f'{msg_label} db "{msg}", 0')

                buf = f"inputbuf_{temp_counter}"
                data_lines.append(f"{buf} db 64 dup(0)")
                temp_counter += 1

                # print message
                text_lines.append(f"    lea rcx, [rel {msg_label}]")
                text_lines.append("    sub rsp, 40")
                text_lines.append("    call printf")
                text_lines.append("    add rsp, 40")

                # scanf string
                text_lines.append(f"    lea rcx, [rel fmt_in]")
                text_lines.append(f"    lea rdx, [rel {buf}]")
                text_lines.append("    sub rsp, 40")
                text_lines.append("    call scanf")
                text_lines.append("    add rsp, 40")

                # is_var=False (buf ist direkt das Label), is_int=False (String)
                return buf, False, False

            else:
                raise ValueError(f"Unbekannte Funktion: {arg.function_name}")

        else:
            raise ValueError(f"Unsupported argument: {type(arg)}")

    def emit_printf_int(ptr):
        text_lines.append("    lea rcx, [rel fmt_int]")
        text_lines.append(f"    mov eax, [rel {ptr}]")
        text_lines.append("    mov rdx, rax")
        text_lines.append("    sub rsp, 40")
        text_lines.append("    call printf")
        text_lines.append("    add rsp, 40")

    def emit_printf_str(ptr, is_var=False):
        text_lines.append("    lea rcx, [rel fmt_str]")
        if is_var:
            # Variable enthält eine Adresse -> dereferenzieren
            text_lines.append(f"    mov rdx, [rel {ptr}]")
        else:
            # Label IST die Adresse
            text_lines.append(f"    lea rdx, [rel {ptr}]")
        text_lines.append("    sub rsp, 40")
        text_lines.append("    call printf")
        text_lines.append("    add rsp, 40")

    def emit_log_call(args):
        for arg in args:
            ptr, is_var, is_int = arg_pointer_operand(arg)
            if is_int:
                emit_printf_int(ptr)
            else:
                emit_printf_str(ptr, is_var=is_var)

    # -------------------------
    # Codegen
    # -------------------------

    def compile_block(statements):
        nonlocal current_for_counter

        for stmt in statements:
            if stmt is None:
                continue

            if isinstance(stmt, CallStatement):

                if stmt.function_name == "defv":
                    i = 0
                    while i < len(stmt.args):
                        name = stmt.args[i]
                        value = stmt.args[i + 1]

                        ptr, _, is_int = arg_pointer_operand(value)
                        vtype = "int" if is_int else "str"
                        ensure_variable(name.name, vtype)

                        if is_int:
                            text_lines.append(f"    mov eax, [rel {ptr}]")
                            text_lines.append(f"    mov [rel {variables[name.name]}], eax")
                        else:
                            text_lines.append(f"    lea rax, [rel {ptr}]")
                            text_lines.append(f"    mov [rel {variables[name.name]}], rax")

                        i += 2

                elif stmt.function_name == "log":
                    emit_log_call(stmt.args)

                elif stmt.function_name == "iniv":
                    for arg in stmt.args:
                        ensure_variable(arg.name)

            elif stmt.__class__.__name__ == "IfNode":
                end_label = new_label("if")

                cond = stmt.condition

                if hasattr(cond, 'op'):
                    left_ptr, left_is_var, left_is_int = arg_pointer_operand(cond.left)
                    right_ptr, right_is_var, right_is_int = arg_pointer_operand(cond.right)

                    # STRING VERGLEICH
                    if not left_is_int or not right_is_int:
                        # Windows x64: RCX = arg1, RDX = arg2
                        if left_is_var:
                            text_lines.append(f"    mov rcx, [rel {left_ptr}]")
                        else:
                            text_lines.append(f"    lea rcx, [rel {left_ptr}]")

                        if right_is_var:
                            text_lines.append(f"    mov rdx, [rel {right_ptr}]")
                        else:
                            text_lines.append(f"    lea rdx, [rel {right_ptr}]")

                        text_lines.append("    sub rsp, 40")
                        text_lines.append("    call strcmp")
                        text_lines.append("    add rsp, 40")
                        text_lines.append("    test eax, eax")

                        if cond.op == "EQ":
                            text_lines.append(f"    jne {end_label}")
                        elif cond.op == "NEQ":
                            text_lines.append(f"    je {end_label}")
                        else:
                            raise ValueError("String unterstützt nur == und !=")

                    # INT VERGLEICH
                    else:
                        text_lines.append(f"    mov eax, [rel {left_ptr}]")
                        text_lines.append(f"    cmp eax, [rel {right_ptr}]")

                        if cond.op == "EQ":
                            text_lines.append(f"    jne {end_label}")
                        elif cond.op == "NEQ":
                            text_lines.append(f"    je {end_label}")
                        elif cond.op == "LTE":
                            text_lines.append(f"    jg {end_label}")
                        elif cond.op == "GTE":
                            text_lines.append(f"    jl {end_label}")

                compile_block(stmt.body)
                text_lines.append(f"{end_label}:")

            elif stmt.__class__.__name__ == "ForNode":
                loop = new_label("for")
                counter = f"{loop}_counter"

                data_lines.append(f"{counter} dd 0")

                text_lines.append(f"    mov dword [rel {counter}], 0")
                text_lines.append(f"{loop}_start:")

                text_lines.append(f"    mov eax, [rel {counter}]")
                text_lines.append(f"    cmp eax, {stmt.counter}")
                text_lines.append(f"    jge {loop}_end")

                old = current_for_counter
                current_for_counter = counter

                compile_block(stmt.body)

                current_for_counter = old

                text_lines.append(f"    inc dword [rel {counter}]")
                text_lines.append(f"    jmp {loop}_start")
                text_lines.append(f"{loop}_end:")

    # -------------------------
    # Start
    # -------------------------

    compile_block(ast_root.statements)

    return "\n".join([
        "default rel",
        "extern printf",
        "extern scanf",
        "extern strcmp",
        "extern atoi",
        "section .data",
        *data_lines,
        "section .text",
        "global main",
        "main:",
        *text_lines,
        "    xor eax, eax",
        "    ret"
    ])