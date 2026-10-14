"""El QR de la entrada en la computadora (`leda.qr`; ADR 0024, decisión 8).

Sin un lector de QR a mano, la prueba lee la matriz como lo hace un lector: la información de
formato (corrección y máscara, con su código BCH), los módulos en zigzag fuera de los patrones
fijos, la máscara deshecha, los bloques desentrelazados, cada bloque con su Reed-Solomon en cero
y, del modo byte, el texto. Si el texto sale igual, la matriz está bien armada.
"""

from __future__ import annotations

import pytest

from leda import qr


def _formato_leido(matriz: list[str]) -> int:
    """Los 15 bits de formato de la primera copia, alrededor del buscador de arriba a la
    izquierda, en el orden en que se escribieron."""
    m = lambda x, y: matriz[y][x] == "1"  # noqa: E731
    lugares = [(8, i) for i in range(6)] + [(8, 7), (8, 8), (7, 8)] + [
        (14 - i, 8) for i in range(9, 15)]
    return sum(1 << i for i, (x, y) in enumerate(lugares) if m(x, y))


def _segunda_copia(matriz: list[str]) -> int:
    tam = len(matriz)
    lugares = [(tam - 1 - i, 8) for i in range(8)] + [(8, tam - 15 + i) for i in range(8, 15)]
    return sum(1 << i for i, (x, y) in enumerate(lugares) if matriz[y][x] == "1")


def _fijos(version: int) -> list[list[bool]]:
    tam = version * 4 + 17
    fija = [[False] * tam for _ in range(tam)]

    def poner(x, y, _oscuro):
        fija[y][x] = True

    qr._patrones_fijos(version, tam, poner)
    return fija


def leer(matriz: list[str]) -> str:
    tam = len(matriz)
    version = (tam - 17) // 4
    formato = _formato_leido(matriz)
    assert formato == _segunda_copia(matriz)
    mascara = next(m for m in range(8) if qr.bits_de_formato(m) == formato)
    fija = _fijos(version)
    bits = [(matriz[y][x] == "1") ^ qr.invierte(mascara, x, y)
            for x, y in qr.recorrido(tam) if not fija[y][x]]
    crudos = qr._modulos_de_datos(version) // 8
    codigos = [int("".join("1" if b else "0" for b in bits[i * 8:i * 8 + 8]), 2)
               for i in range(crudos)]
    bloques_n = qr._BLOQUES_M[version]
    ecc = qr._ECC_POR_BLOQUE_M[version]
    cortos = bloques_n - crudos % bloques_n
    largo_corto = crudos // bloques_n
    largos = [largo_corto - ecc + (0 if i < cortos else 1) for i in range(bloques_n)]
    bloques: list[list[int]] = [[] for _ in range(bloques_n)]
    k = 0
    for i in range(max(largos)):
        for j in range(bloques_n):
            if i < largos[j]:
                bloques[j].append(codigos[k])
                k += 1
    for i in range(ecc):
        for j in range(bloques_n):
            bloques[j].append(codigos[k])
            k += 1
    generador = qr.divisor(ecc)
    datos: list[int] = []
    for j, bloque in enumerate(bloques):
        assert qr.resto(bloque, generador) == [0] * ecc, f"el bloque {j} no verifica"
        datos += bloque[:largos[j]]
    flujo = "".join(f"{b:08b}" for b in datos)
    assert flujo[:4] == "0100"
    ancho = 8 if version <= 9 else 16
    largo = int(flujo[4:4 + ancho], 2)
    inicio = 4 + ancho
    return bytes(int(flujo[inicio + 8 * i:inicio + 8 * i + 8], 2)
                 for i in range(largo)).decode("utf-8")


@pytest.mark.parametrize("texto", [
    "https://t.me/Leda_PM_bot?start=compu_" + "A1b2_C3d-" * 3 + "xyzw",
    "https://t.me/Leda_Admin_bot?start=compu_" + "Z" * 32,
    "hola",
    "x" * 150,                      # una versión de 7 a 10, con información de versión
])
def test_la_matriz_se_lee_igual_que_el_texto(texto):
    matriz = qr.modulos(texto)
    assert all(len(fila) == len(matriz) for fila in matriz)
    assert leer(matriz) == texto


def test_los_buscadores_estan_en_tres_esquinas():
    matriz = qr.modulos("https://t.me/Leda_PM_bot?start=compu_abc")
    tam = len(matriz)
    for cx, cy in ((0, 0), (tam - 7, 0), (0, tam - 7)):
        assert matriz[cy][cx:cx + 7] == "1111111"
        assert matriz[cy + 1][cx:cx + 7] == "1000001"
        assert matriz[cy + 3][cx:cx + 7] == "1011101"


def test_un_texto_demasiado_largo_se_rechaza():
    with pytest.raises(qr.DemasiadoLargo):
        qr.modulos("x" * 300)


def test_la_informacion_de_formato_y_de_version_son_las_de_la_norma():
    """Los valores de la tabla de la norma (corrección M, máscaras 0 a 7; versiones 7 y 10)."""
    assert [qr.bits_de_formato(m) for m in range(8)] == [
        0b101010000010010, 0b101000100100101, 0b101111001111100, 0b101101101001011,
        0b100010111111001, 0b100000011001110, 0b100111110010111, 0b100101010100000]
    assert qr.bits_de_version(7) == 0x07C94
    assert qr.bits_de_version(10) == 0x0A4D3
