default rel
extern printf
extern scanf
extern strcmp
extern atoi
section .data
fmt_int db "%d", 10, 0
fmt_str db "%s", 10, 0
fmt_in db "%s", 0
var_x dq 0
var_y dq 0
var_operator dq 0
var_ergebnis dq 0
msg_7 db "The first number: ", 0
inputbuf_0 db 64 dup(0)
tmp_1 dd 0
msg_10 db "The second number: ", 0
inputbuf_2 db 64 dup(0)
tmp_3 dd 0
msg_13 db "The operator for the numbers: ", 0
inputbuf_4 db 64 dup(0)
str_5 db "+", 0
tmp_6 dd 0
str_7 db "-", 0
tmp_8 dd 0
str_9 db "/", 0
tmp_10 dd 0
str_11 db "*", 0
tmp_12 dd 0
str_13 db "Ergebnis: ", 0
section .text
global main
main:
    lea rcx, [rel msg_7]
    sub rsp, 40
    call printf
    add rsp, 40
    lea rcx, [rel fmt_in]
    lea rdx, [rel inputbuf_0]
    sub rsp, 40
    call scanf
    add rsp, 40
    lea rcx, [rel inputbuf_0]
    sub rsp, 40
    call atoi
    add rsp, 40
    mov [rel tmp_1], eax
    mov eax, [rel tmp_1]
    mov [rel var_x], eax
    lea rcx, [rel msg_10]
    sub rsp, 40
    call printf
    add rsp, 40
    lea rcx, [rel fmt_in]
    lea rdx, [rel inputbuf_2]
    sub rsp, 40
    call scanf
    add rsp, 40
    lea rcx, [rel inputbuf_2]
    sub rsp, 40
    call atoi
    add rsp, 40
    mov [rel tmp_3], eax
    mov eax, [rel tmp_3]
    mov [rel var_y], eax
    lea rcx, [rel msg_13]
    sub rsp, 40
    call printf
    add rsp, 40
    lea rcx, [rel fmt_in]
    lea rdx, [rel inputbuf_4]
    sub rsp, 40
    call scanf
    add rsp, 40
    lea rax, [rel inputbuf_4]
    mov [rel var_operator], rax
    mov rcx, [rel var_operator]
    lea rdx, [rel str_5]
    sub rsp, 40
    call strcmp
    add rsp, 40
    test eax, eax
    jne if_1
    mov eax, [rel var_x]
    add eax, [rel var_y]
    mov [rel tmp_6], eax
    mov eax, [rel tmp_6]
    mov [rel var_ergebnis], eax
if_1:
    mov rcx, [rel var_operator]
    lea rdx, [rel str_7]
    sub rsp, 40
    call strcmp
    add rsp, 40
    test eax, eax
    jne if_2
    mov eax, [rel var_x]
    sub eax, [rel var_y]
    mov [rel tmp_8], eax
    mov eax, [rel tmp_8]
    mov [rel var_ergebnis], eax
if_2:
    mov rcx, [rel var_operator]
    lea rdx, [rel str_9]
    sub rsp, 40
    call strcmp
    add rsp, 40
    test eax, eax
    jne if_3
    mov eax, [rel var_x]
    cdq
    idiv dword [rel var_y]
    mov [rel tmp_10], eax
    mov eax, [rel tmp_10]
    mov [rel var_ergebnis], eax
if_3:
    mov rcx, [rel var_operator]
    lea rdx, [rel str_11]
    sub rsp, 40
    call strcmp
    add rsp, 40
    test eax, eax
    jne if_4
    mov eax, [rel var_x]
    imul eax, [rel var_y]
    mov [rel tmp_12], eax
    mov eax, [rel tmp_12]
    mov [rel var_ergebnis], eax
if_4:
    lea rcx, [rel fmt_str]
    lea rdx, [rel str_13]
    sub rsp, 40
    call printf
    add rsp, 40
    lea rcx, [rel fmt_int]
    mov eax, [rel var_ergebnis]
    mov rdx, rax
    sub rsp, 40
    call printf
    add rsp, 40
    xor eax, eax
    ret