section .data
float_const_0: .float 3.5
str_1: .asciz "Resultado: "
section .text
global _start
_start:
  li a7, 6
  ecall
  fmv.s ft8, fa0
  flw ft0, float_const_0
  fadd.s ft2, ft8, ft0
  fmv.s ft9, ft2
  la a0, str_1
  li a7, 4
  ecall
  fmv.s fa0, ft9
  li a7, 2
  ecall
  li a0, 10
  li a7, 11
  ecall
  li a7, 10
  ecall

# Funciones matemáticas básicas
sin:
  # Implementación simple (debería usar librería matemática)
  fmv.s fa0, fa0  # Placeholder
  ret
cos:
  fmv.s fa0, fa0
  ret
tan:
  fmv.s fa0, fa0
  ret