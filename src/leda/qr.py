"""El QR de la entrada en la computadora (ADR 0024, decisión 8), sin dependencias.

La web de la computadora muestra un QR con el enlace `https://t.me/<bot>?start=<código>`: se
escanea con la cámara del celular y Telegram abre el chat de Leda. Un enlace así entra en una
versión chica (unos 80 bytes), así que este módulo codifica sólo lo que hace falta: modo byte,
corrección de errores M (se recupera hasta un 15 % de los módulos) y versiones 1 a 10 (hasta 213
bytes). Sigue la norma ISO/IEC 18004 como la implementa la biblioteca de Project Nayuki (licencia
MIT): Reed-Solomon sobre GF(256), los patrones fijos, la información de formato y de versión, el
recorrido en zigzag y la máscara de menor penalidad.

`modulos(texto)` devuelve la matriz como renglones de "0" y "1" (oscuro), sin la zona en blanco
de alrededor: la web la dibuja (cuatro módulos de margen, oscuro sobre claro).
"""

from __future__ import annotations

# Por versión (índice 0 sin uso), para la corrección M.
_ECC_POR_BLOQUE_M = (-1, 10, 16, 26, 18, 24, 16, 18, 22, 22, 26)
_BLOQUES_M = (-1, 1, 1, 1, 2, 2, 4, 4, 4, 5, 5)
# Los bits de formato de la corrección M.
_FORMATO_M = 0
VERSION_MAXIMA = 10


class DemasiadoLargo(ValueError):
    """El texto no entra en la versión más grande que se codifica."""


def modulos(texto: str) -> list[str]:
    """La matriz del QR de `texto` (UTF-8, modo byte, corrección M), renglón por renglón."""
    datos = texto.encode("utf-8")
    version = _version_para(len(datos))
    tam = version * 4 + 17
    matriz = [[False] * tam for _ in range(tam)]
    fija = [[False] * tam for _ in range(tam)]

    def poner(x: int, y: int, oscuro: bool) -> None:
        matriz[y][x] = oscuro
        fija[y][x] = True

    _patrones_fijos(version, tam, poner)
    codigos = _con_correccion(version, _codificar(datos, version))
    _dibujar_codigos(tam, matriz, fija, codigos)
    mejor, penalidad_minima = 0, None
    for mascara in range(8):
        _aplicar_mascara(tam, matriz, fija, mascara)
        _formato(tam, poner, mascara)
        penalidad = _penalidad(tam, matriz)
        if penalidad_minima is None or penalidad < penalidad_minima:
            mejor, penalidad_minima = mascara, penalidad
        _aplicar_mascara(tam, matriz, fija, mascara)          # la deshace (XOR)
    _aplicar_mascara(tam, matriz, fija, mejor)
    _formato(tam, poner, mejor)
    return ["".join("1" if m else "0" for m in fila) for fila in matriz]


# --- Los datos --------------------------------------------------------------------------------

def _modulos_de_datos(version: int) -> int:
    """Cuántos módulos quedan para datos y corrección, sin los patrones fijos."""
    resultado = (16 * version + 128) * version + 64
    if version >= 2:
        alineacion = version // 7 + 2
        resultado -= (25 * alineacion - 10) * alineacion - 55
        if version >= 7:
            resultado -= 36
    return resultado


def _codigos_de_datos(version: int) -> int:
    return (_modulos_de_datos(version) // 8
            - _ECC_POR_BLOQUE_M[version] * _BLOQUES_M[version])


def _bits_del_largo(version: int) -> int:
    return 8 if version <= 9 else 16


def _version_para(largo: int) -> int:
    for version in range(1, VERSION_MAXIMA + 1):
        if 4 + _bits_del_largo(version) + 8 * largo <= _codigos_de_datos(version) * 8:
            return version
    raise DemasiadoLargo(f"{largo} bytes no entran en un QR de versión {VERSION_MAXIMA}")


def _codificar(datos: bytes, version: int) -> list[int]:
    bits: list[int] = []

    def agregar(valor: int, cuantos: int) -> None:
        bits.extend((valor >> i) & 1 for i in reversed(range(cuantos)))

    agregar(0b0100, 4)                                  # modo byte
    agregar(len(datos), _bits_del_largo(version))
    for b in datos:
        agregar(b, 8)
    capacidad = _codigos_de_datos(version) * 8
    agregar(0, min(4, capacidad - len(bits)))          # el terminador
    agregar(0, -len(bits) % 8)
    relleno = 0xEC
    while len(bits) < capacidad:
        agregar(relleno, 8)
        relleno ^= 0xEC ^ 0x11
    return [int("".join(map(str, bits[i:i + 8])), 2) for i in range(0, len(bits), 8)]


# --- Reed-Solomon -------------------------------------------------------------------------------

def _multiplicar(x: int, y: int) -> int:
    z = 0
    for i in reversed(range(8)):
        z = (z << 1) ^ ((z >> 7) * 0x11D)
        z ^= ((y >> i) & 1) * x
    return z


def divisor(grado: int) -> list[int]:
    """El polinomio generador de Reed-Solomon de ese grado (sin el coeficiente principal)."""
    resultado = [0] * (grado - 1) + [1]
    raiz = 1
    for _ in range(grado):
        for j in range(grado):
            resultado[j] = _multiplicar(resultado[j], raiz)
            if j + 1 < grado:
                resultado[j] ^= resultado[j + 1]
        raiz = _multiplicar(raiz, 0x02)
    return resultado


def resto(datos: list[int], generador: list[int]) -> list[int]:
    """El resto de dividir `datos` por el generador: la corrección de un bloque (o ceros, si el
    bloque entero ya la tiene)."""
    resultado = [0] * len(generador)
    for b in datos:
        factor = b ^ resultado.pop(0)
        resultado.append(0)
        for i, coeficiente in enumerate(generador):
            resultado[i] ^= _multiplicar(coeficiente, factor)
    return resultado


def _con_correccion(version: int, datos: list[int]) -> list[int]:
    bloques_n = _BLOQUES_M[version]
    ecc = _ECC_POR_BLOQUE_M[version]
    crudos = _modulos_de_datos(version) // 8
    cortos = bloques_n - crudos % bloques_n
    largo_corto = crudos // bloques_n
    generador = divisor(ecc)
    bloques, k = [], 0
    for i in range(bloques_n):
        tramo = datos[k:k + largo_corto - ecc + (0 if i < cortos else 1)]
        k += len(tramo)
        correccion = resto(tramo, generador)
        if i < cortos:
            tramo = tramo + [0]
        bloques.append(tramo + correccion)
    resultado = []
    for i in range(len(bloques[0])):
        for j, bloque in enumerate(bloques):
            if i != largo_corto - ecc or j >= cortos:
                resultado.append(bloque[i])
    return resultado


# --- La matriz ----------------------------------------------------------------------------------

def posiciones_de_alineacion(version: int) -> list[int]:
    if version == 1:
        return []
    cuantas = version // 7 + 2
    paso = (version * 8 + cuantas * 3 + 5) // (cuantas * 4 - 4) * 2
    tam = version * 4 + 17
    return list(reversed([tam - 7 - i * paso for i in range(cuantas - 1)] + [6]))


def _patrones_fijos(version: int, tam: int, poner) -> None:
    for i in range(tam):
        poner(6, i, i % 2 == 0)
        poner(i, 6, i % 2 == 0)
    for cx, cy in ((3, 3), (tam - 4, 3), (3, tam - 4)):
        for dy in range(-4, 5):
            for dx in range(-4, 5):
                x, y = cx + dx, cy + dy
                if 0 <= x < tam and 0 <= y < tam:
                    poner(x, y, max(abs(dx), abs(dy)) not in (2, 4))
    alineacion = posiciones_de_alineacion(version)
    ultima = len(alineacion) - 1
    for i, ax in enumerate(alineacion):
        for j, ay in enumerate(alineacion):
            if (i, j) in ((0, 0), (0, ultima), (ultima, 0)):
                continue
            for dy in range(-2, 3):
                for dx in range(-2, 3):
                    poner(ax + dx, ay + dy, max(abs(dx), abs(dy)) != 1)
    _formato(tam, poner, 0)               # reserva su lugar; se escribe con la máscara elegida
    if version >= 7:
        bits = bits_de_version(version)
        for i in range(18):
            oscuro = (bits >> i) & 1 == 1
            a, b = tam - 11 + i % 3, i // 3
            poner(a, b, oscuro)
            poner(b, a, oscuro)


def bits_de_version(version: int) -> int:
    """Los 18 bits de la información de versión (versiones 7 en adelante), con su código BCH."""
    resto_ = version
    for _ in range(12):
        resto_ = (resto_ << 1) ^ ((resto_ >> 11) * 0x1F25)
    return version << 12 | resto_


def bits_de_formato(mascara: int) -> int:
    datos = _FORMATO_M << 3 | mascara
    resto_ = datos
    for _ in range(10):
        resto_ = (resto_ << 1) ^ ((resto_ >> 9) * 0x537)
    return (datos << 10 | resto_) ^ 0x5412


def _formato(tam: int, poner, mascara: int) -> None:
    bits = bits_de_formato(mascara)

    def bit(i: int) -> bool:
        return (bits >> i) & 1 == 1

    for i in range(6):
        poner(8, i, bit(i))
    poner(8, 7, bit(6))
    poner(8, 8, bit(7))
    poner(7, 8, bit(8))
    for i in range(9, 15):
        poner(14 - i, 8, bit(i))
    for i in range(8):
        poner(tam - 1 - i, 8, bit(i))
    for i in range(8, 15):
        poner(8, tam - 15 + i, bit(i))
    poner(8, tam - 8, True)


def recorrido(tam: int):
    """Las posiciones `(x, y)` en el orden en que van los bits: de a dos columnas, de derecha a
    izquierda, subiendo y bajando, salteando la columna del patrón de tiempo."""
    derecha = tam - 1
    while derecha >= 1:
        if derecha == 6:
            derecha = 5
        for vertical in range(tam):
            for j in range(2):
                x = derecha - j
                sube = ((derecha + 1) & 2) == 0
                y = tam - 1 - vertical if sube else vertical
                yield x, y
        derecha -= 2


def _dibujar_codigos(tam: int, matriz, fija, codigos: list[int]) -> None:
    i = 0
    for x, y in recorrido(tam):
        if not fija[y][x] and i < len(codigos) * 8:
            matriz[y][x] = (codigos[i >> 3] >> (7 - (i & 7))) & 1 == 1
            i += 1


def invierte(mascara: int, x: int, y: int) -> bool:
    return (
        (x + y) % 2 == 0,
        y % 2 == 0,
        x % 3 == 0,
        (x + y) % 3 == 0,
        (x // 3 + y // 2) % 2 == 0,
        x * y % 2 + x * y % 3 == 0,
        (x * y % 2 + x * y % 3) % 2 == 0,
        ((x + y) % 2 + x * y % 3) % 2 == 0,
    )[mascara]


def _aplicar_mascara(tam: int, matriz, fija, mascara: int) -> None:
    for y in range(tam):
        for x in range(tam):
            if not fija[y][x] and invierte(mascara, x, y):
                matriz[y][x] = not matriz[y][x]


def _penalidad(tam: int, matriz) -> int:
    """Una penalidad simplificada (renglones iguales, bloques de 2x2 y equilibrio de oscuros):
    cualquier máscara se lee igual; ésta sólo elige la más pareja."""
    total = 0
    for linea in [*matriz, *([matriz[y][x] for y in range(tam)] for x in range(tam))]:
        corrida, anterior = 0, None
        for m in linea:
            if m == anterior:
                corrida += 1
            else:
                if corrida >= 5:
                    total += corrida - 2
                corrida, anterior = 1, m
        if corrida >= 5:
            total += corrida - 2
    for y in range(tam - 1):
        for x in range(tam - 1):
            if matriz[y][x] == matriz[y][x + 1] == matriz[y + 1][x] == matriz[y + 1][x + 1]:
                total += 3
    oscuros = sum(sum(fila) for fila in matriz)
    total += abs(oscuros * 20 - tam * tam * 10) // (tam * tam) * 10
    return total
