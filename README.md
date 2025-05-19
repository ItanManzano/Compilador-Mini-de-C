 🚀 Compilador de Pseudo-C a RISC-V

**Un compilador educativo** que traduce un subconjunto de C a código ensamblador RISC-V (RV32I), diseñado para la materia de Compiladores. Optimiza el uso de registros y genera código compatible con RARS.

 🔍 Características Principales

 ✅ Lenguaje Fuente Soportado
- **Tipos de datos**: `int`, `float`, `char`, `string`
- **Estructuras básicas**:
  - Declaraciones: `var float x;`
  - Operaciones aritméticas: `y = (x + 3.5) / 2;`
  - Entrada/salida: `read(x);`, `println("Resultado:", y);`
  - Ciclos: `for (i = 0; 5) { ... }`
  - Funciones intrínsecas: `sin(x)`, `cos(x)`, `tan(x)`

 🛠️ Tecnologías Clave
- **Python 3**: Análisis léxico/sintáctico y generación de código.
- **RISC-V**: Arquitectura objetivo (RV32I).
- **RARS**: Simulador para ejecutar el código generado.

 ⚙️ Funcionamiento Interno
1. **Fases de compilación**:
   - Eliminación de comentarios (`/* ... */`).
   - Tabla de símbolos para gestión de variables.
   - Traducción a código intermedio.
   - Asignación óptima de registros (`ft0-ft7` para floats, `t0-t6` para enteros).

2. **Generación de código**:
   - Syscalls RISC-V para E/S.
   - Operaciones float/int con detección automática de tipos.
   - Manejo de strings en `.data`.

 📦 Instalación y Uso

 Requisitos
- Python 3.8+
- RARS (opcional, para ejecución)

```bash
# Clonar repositorio
git clone https://github.com/tu-usuario/mini-compilador-c.git
cd mini-compilador-c

# Ejecutar compilador
python compilador.py < archivo_entrada.txt > salida.s

# Ejecutar en RARS (opcional)
java -jar rars.jar salida.s
```

 📝 Ejemplo de Entrada/Salida

**Entrada (`ejemplo.c`)**:
```c
var float x, y;
print("Ingrese x: ");
read(x);
y = sin(x) + 3.5;
println("Resultado:", y);
end.
```

**Salida (`salida.s`)**:
```asm
section .data
str_0: .asciz "Ingrese x: "
str_1: .asciz "Resultado:"
float_const_0: .float 3.5

section .text
global _start
_start:
    la a0, str_0
    li a7, 4
    ecall
    li a7, 6
    ecall
    fmv.s ft0, fa0
    call sin
    fmv.s ft1, fa0
    flw ft2, float_const_0
    fadd.s ft3, ft1, ft2
    # ... (resto del código)
```

 🎯 Objetivos del Proyecto
- Demostrar los principios de compilación (análisis → síntesis).
- Generar código RISC-V eficiente.
- Servir como herramienta educativa para cursos de compiladores.

 📌 Notas Adicionales
- **Limitaciones**: No maneja funciones definidas por el usuario ni arreglos.
- **Extensible**: Diseñado para añadir nuevas características fácilmente.


---


