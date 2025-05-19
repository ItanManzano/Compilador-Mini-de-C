import re
from collections import OrderedDict

class Compilador:
    def __init__(self):
        self.tabla_simbolos = OrderedDict()
        self.registros_float = [f'ft{i}' for i in range(8, 16)]
        self.registros_int = [f't{i}' for i in range(1, 7)]
        self.seccion_datos = []
        self.seccion_texto = []
        self.contador_etiquetas = 0
        self.constantes_float = {}

    def agregar_constante_float(self, valor):
        if valor not in self.constantes_float:
            etiqueta = f'float_const_{self.contador_etiquetas}'
            self.contador_etiquetas += 1
            self.seccion_datos.append(f'{etiqueta}: .float {valor}')
            self.constantes_float[valor] = etiqueta
        return self.constantes_float[valor]

    def agregar_variable(self, nombre, tipo):
        if nombre in self.tabla_simbolos:
            raise ValueError(f"Variable '{nombre}' ya declarada")
        
        if tipo == 'float':
            reg = self.registros_float.pop(0) if self.registros_float else f'mem_{nombre}'
        else:  # int
            reg = self.registros_int.pop(0) if self.registros_int else f'mem_{nombre}'
        
        self.tabla_simbolos[nombre] = {'tipo': tipo, 'reg': reg}
        return reg

    def generar_lectura(self, variable):
        var = self.tabla_simbolos[variable]
        if var['tipo'] == 'float':
            return '\n'.join(['  li a7, 6', '  ecall', f'  fmv.s {var["reg"]}, fa0'])
        else:  # int
            return '\n'.join(['  li a7, 5', '  ecall', f'  mv {var["reg"]}, a0'])

    def generar_impresion(self, args, nueva_linea=False):
        codigo = []
        for arg in args:
            arg = arg.strip()
            if arg.startswith('"'):
                etiqueta = f'str_{self.contador_etiquetas}'
                self.contador_etiquetas += 1
                self.seccion_datos.append(f'{etiqueta}: .asciz {arg}')
                codigo.extend([f'  la a0, {etiqueta}', '  li a7, 4', '  ecall'])
            else:
                var = self.tabla_simbolos[arg]
                if var['tipo'] == 'float':
                    codigo.extend([f'  fmv.s fa0, {var["reg"]}', '  li a7, 2', '  ecall'])
                else:
                    codigo.extend([f'  mv a0, {var["reg"]}', '  li a7, 1', '  ecall'])
        
        if nueva_linea:
            codigo.extend(['  li a0, 10', '  li a7, 11', '  ecall'])
        return '\n'.join(codigo)

    def evaluar_expresion(self, expresion):
        # Nueva versión que soporta expresiones como "x + 3.5"
        expresion = expresion.strip()
        
        # Buscar operadores en orden de precedencia
        for op in ['+', '-', '*', '/']:
            if op in expresion:
                izquierda, derecha = expresion.split(op, 1)
                izquierda = izquierda.strip()
                derecha = derecha.strip()
                
                # Determinar tipo de operación
                es_float = any(
                    '.' in x or 
                    (x in self.tabla_simbolos and self.tabla_simbolos[x]['tipo'] == 'float')
                    for x in [izquierda, derecha]
                )
                
                # Código para cada operando
                codigo = []
                def cargar_operando(op):
                    if op in self.tabla_simbolos:
                        return self.tabla_simbolos[op]['reg'], []
                    elif '.' in op:
                        etiqueta = self.agregar_constante_float(op)
                        reg = 'ft0' if es_float else 't0'
                        return reg, [f'  flw {reg}, {etiqueta}']
                    else:
                        reg = 'ft0' if es_float else 't0'
                        return reg, [f'  li {reg}, {int(op)}']
                
                reg_izq, cod_izq = cargar_operando(izquierda)
                reg_der, cod_der = cargar_operando(derecha)
                
                codigo.extend(cod_izq)
                codigo.extend(cod_der)
                
                # Operación
                reg_res = 'ft2' if es_float else 't2'
                if es_float:
                    ops = {'+': 'fadd.s', '-': 'fsub.s', '*': 'fmul.s', '/': 'fdiv.s'}
                else:
                    ops = {'+': 'add', '-': 'sub', '*': 'mul', '/': 'div'}
                
                codigo.append(f'  {ops[op]} {reg_res}, {reg_izq}, {reg_der}')
                
                return reg_res, '\n'.join(codigo)
        
        # Si no hay operador, es un solo valor
        if expresion in self.tabla_simbolos:
            return self.tabla_simbolos[expresion]['reg'], ''
        elif '.' in expresion:
            etiqueta = self.agregar_constante_float(expresion)
            return 'ft0', f'  flw ft0, {etiqueta}'
        else:
            return 't0', f'  li t0, {int(expresion)}'

    def compilar(self, codigo_fuente):
        lineas = [linea.strip() for linea in codigo_fuente.split('\n') 
                 if linea.strip() and not linea.strip().startswith('//')]

        # Fase 1: Declaraciones
        for linea in lineas:
            if linea.startswith('var '):
                partes = linea.split()
                if len(partes) >= 3:  # var tipo nombre
                    self.agregar_variable(partes[2], partes[1])

        # Fase 2: Generación de código
        i = 0
        while i < len(lineas):
            linea = lineas[i]
            try:
                if linea.startswith('print('):
                    args = linea[6:-1].split(',')
                    self.seccion_texto.append(self.generar_impresion(args))
                elif linea.startswith('println('):
                    args = linea[8:-1].split(',')
                    self.seccion_texto.append(self.generar_impresion(args, True))
                elif linea.startswith('read('):
                    var = linea[5:-1].strip()
                    self.seccion_texto.append(self.generar_lectura(var))
                elif '=' in linea and not linea.startswith('var '):
                    var, expr = linea.split('=', 1)
                    var = var.strip()
                    reg, codigo = self.evaluar_expresion(expr.strip())
                    tipo = self.tabla_simbolos[var]['tipo']
                    if tipo == 'float':
                        self.seccion_texto.append(f'{codigo}\n  fmv.s {self.tabla_simbolos[var]["reg"]}, {reg}')
                    else:
                        self.seccion_texto.append(f'{codigo}\n  mv {self.tabla_simbolos[var]["reg"]}, {reg}')
                elif linea == 'end.':
                    self.seccion_texto.append('  li a7, 10\n  ecall')
            except Exception as e:
                raise ValueError(f"Error en línea {i+1}: '{linea}'\nDetalle: {str(e)}")
            i += 1

        # Ensamblar código final
        codigo_ensamblador = [
            'section .data',
            *self.seccion_datos,
            'section .text',
            'global _start',
            '_start:',
            *self.seccion_texto,
            '',
            '# Funciones matemáticas básicas',
            'sin:',
            '  # Implementación simple (debería usar librería matemática)',
            '  fmv.s fa0, fa0  # Placeholder',
            '  ret',
            'cos:',
            '  fmv.s fa0, fa0',
            '  ret',
            'tan:',
            '  fmv.s fa0, fa0',
            '  ret'
        ]
        return '\n'.join(codigo_ensamblador)

# Ejemplo de uso
if __name__ == "__main__":
    compilador = Compilador()
    programa = """
    var float x
    var float y
    read(x)
    y = x + 3.5
    println("Resultado: ", y)
    end.
    """
    try:
        resultado = compilador.compilar(programa)
        print("✅ Compilación exitosa!")
        print(resultado)
        with open("output.s", "w") as f:
            f.write(resultado)
    except Exception as e:
        print(f"❌ Error: {e}")