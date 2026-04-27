default rel
extern printf
section .data
fmt_str db "%s", 0
fmt_int db "%d", 0
space_str db " ", 0
nl_str db 10, 0
nil_str db "<nil>", 0
var_x dq nil_str
var_y dq nil_str
str_0 db "Hello", 0
str_1 db "", 0
var_counter dq nil_str
var_for_limit_0 dq 5
section .text
global main
main:
    lea rax, [rel str_0]
    mov [rel var_x], rax
    lea rax, [rel str_1]
    mov [rel var_y], rax
    sub rsp, 8                 ; var_i reservieren
    mov qword [rsp], 0         ; var_i = 0
for_start_0:
    mov rax, [rsp]
    cmp rax, [rel var_for_limit_0]
    jge for_end_0
    mov rax, [rsp]
    mov [rel var_counter], rax
    sub rsp, 40
    lea rcx, [rel fmt_str]
    mov rdx, [rel var_counter]
    call printf
    add rsp, 40
    sub rsp, 40
    lea rcx, [rel fmt_str]
    lea rdx, [rel nl_str]
    call printf
    add rsp, 40
    add qword [rsp], 1
    jmp for_start_0
for_end_0:
    add rsp, 8
    xor eax, eax
    ret