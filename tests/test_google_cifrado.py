"""Cifrado de credenciales de Google (rama auxiliar, G2a).

Todas las claves de estas pruebas se generan acá mismo: ninguna lee ni
imprime el entorno real.
"""

from __future__ import annotations

import pytest
from cryptography.fernet import Fernet

import prisma.cli as cli
from prisma.google import cifrado
from prisma.google.cifrado import (
    ClaveCredencialesAusente, ClaveCredencialesInvalida, ErrorCifrado,
    TokenNoDescifrable,
)


def _clave() -> str:
    return Fernet.generate_key().decode("ascii")


def _linea_clave(salida: str) -> str:
    """La clave impresa: la primera línea no vacía después del encabezado."""
    lineas = salida.splitlines()
    encabezado = next(i for i, l in enumerate(lineas)
                      if l.startswith("Clave nueva"))
    return next(l.strip() for l in lineas[encabezado + 1:] if l.strip())


def test_una_sola_clave_construye_el_cifrador():
    clave = _clave()
    c = cifrado.desde_texto(clave)
    assert c.descifrar(c.cifrar("hola")) == b"hola"


def test_varias_claves_con_espacios_se_recortan():
    a, b = _clave(), _clave()
    c = cifrado.desde_texto(f"  {a} ,\t{b}\n")
    token_de_b = Fernet(b.encode()).encrypt(b"dato")
    assert c.descifrar(token_de_b) == b"dato"


def test_la_primera_clave_cifra_y_todas_descifran():
    vieja, nueva = _clave(), _clave()
    token_viejo = cifrado.desde_texto(vieja).cifrar("secreto")
    c = cifrado.desde_texto(f"{nueva},{vieja}")
    assert c.descifrar(token_viejo) == b"secreto"
    token_nuevo = c.cifrar("otro")
    # Cifró la primera: sólo con la clave nueva se descifra.
    assert Fernet(nueva.encode()).decrypt(token_nuevo) == b"otro"
    with pytest.raises(Exception):
        Fernet(vieja.encode()).decrypt(token_nuevo)


@pytest.mark.parametrize("crudo", ["", "   ", None])
def test_clave_ausente_o_vacia_falla_tipado(crudo):
    with pytest.raises(ClaveCredencialesAusente):
        cifrado.desde_texto(crudo)


@pytest.mark.parametrize("plantilla", ["{a},", ",{a}", "{a},,{a}", "{a}, ,{a}"])
def test_una_entrada_vacia_entre_comas_se_rechaza(plantilla):
    a = _clave()
    with pytest.raises(ClaveCredencialesInvalida):
        cifrado.desde_texto(plantilla.format(a=a))


def test_clave_mal_formada_falla_sin_filtrar_la_clave():
    basura = "esto-no-es-una-clave-fernet-SECRETO123"
    with pytest.raises(ClaveCredencialesInvalida) as e:
        cifrado.desde_texto(f"{_clave()},{basura}")
    assert basura not in str(e.value)
    assert "SECRETO123" not in repr(e.value)


def test_los_errores_comparten_una_base():
    for tipo in (ClaveCredencialesAusente, ClaveCredencialesInvalida,
                 TokenNoDescifrable):
        assert issubclass(tipo, ErrorCifrado)


def test_ida_y_vuelta_de_texto_y_bytes():
    c = cifrado.desde_texto(_clave())
    assert c.descifrar(c.cifrar("ñandú")) == "ñandú".encode("utf-8")
    assert c.descifrar_texto(c.cifrar("ñandú")) == "ñandú"
    assert c.descifrar(c.cifrar(b"\x00\xff")) == b"\x00\xff"


def test_el_token_no_contiene_el_texto_plano():
    c = cifrado.desde_texto(_clave())
    token = c.cifrar("refresh-token-de-prueba")
    assert isinstance(token, bytes)
    assert b"refresh-token-de-prueba" not in token


def test_descifrar_texto_de_bytes_que_no_son_utf8_falla_tipado():
    c = cifrado.desde_texto(_clave())
    token = c.cifrar(b"\xff\xfe\x00")
    with pytest.raises(TokenNoDescifrable) as e:
        c.descifrar_texto(token)
    assert isinstance(e.value, ErrorCifrado)
    assert not isinstance(e.value, UnicodeDecodeError)
    assert "\xff" not in str(e.value) + repr(e.value)


def test_tipo_no_soportado_se_rechaza():
    c = cifrado.desde_texto(_clave())
    with pytest.raises(TypeError):
        c.cifrar(123)  # type: ignore[arg-type]


def test_token_de_una_clave_desconocida_falla_tipado_sin_filtrar():
    ajena = _clave()
    token = cifrado.desde_texto(ajena).cifrar("plano-confidencial")
    c = cifrado.desde_texto(_clave())
    with pytest.raises(TokenNoDescifrable) as e:
        c.descifrar(token)
    texto = str(e.value) + repr(e.value)
    assert ajena not in texto
    assert "plano-confidencial" not in texto
    assert token.decode() not in texto


def test_token_corrupto_falla_tipado():
    c = cifrado.desde_texto(_clave())
    with pytest.raises(TokenNoDescifrable):
        c.descifrar(b"no-es-un-token")


def test_rotar_recifra_bajo_la_clave_actual():
    vieja, nueva = _clave(), _clave()
    token_viejo = cifrado.desde_texto(vieja).cifrar("secreto")
    c = cifrado.desde_texto(f"{nueva},{vieja}")
    rotado = c.rotar(token_viejo)
    assert rotado != token_viejo
    # Ahora se descifra con la clave nueva sola.
    assert cifrado.desde_texto(nueva).descifrar(rotado) == b"secreto"


def test_rotar_un_token_desconocido_falla_tipado():
    c = cifrado.desde_texto(_clave())
    ajeno = cifrado.desde_texto(_clave()).cifrar("x")
    with pytest.raises(TokenNoDescifrable):
        c.rotar(ajeno)


def test_el_cargador_lee_la_variable_de_entorno(monkeypatch):
    clave = _clave()
    monkeypatch.setenv(cifrado.VARIABLE_CLAVE, clave)
    c = cifrado.cargar()
    assert c.descifrar(c.cifrar("ok")) == b"ok"


def test_el_cargador_sin_variable_falla_y_nunca_sigue_sin_cifrar(monkeypatch):
    monkeypatch.delenv(cifrado.VARIABLE_CLAVE, raising=False)
    with pytest.raises(ClaveCredencialesAusente) as e:
        cifrado.cargar()
    assert cifrado.VARIABLE_CLAVE in str(e.value)


def test_el_cargador_con_variable_vacia_falla(monkeypatch):
    monkeypatch.setenv(cifrado.VARIABLE_CLAVE, "  ")
    with pytest.raises(ClaveCredencialesAusente):
        cifrado.cargar()


def test_el_cifrador_no_muestra_las_claves_en_su_repr():
    clave = _clave()
    c = cifrado.desde_texto(clave)
    assert clave not in repr(c)
    assert clave not in str(c)


def test_google_clave_nueva_imprime_una_clave_fernet_valida(capsys, tmp_path,
                                                            monkeypatch):
    monkeypatch.chdir(tmp_path)
    codigo = cli.main(["google", "clave-nueva"])
    salida = capsys.readouterr().out
    assert codigo == 0
    clave = _linea_clave(salida)
    Fernet(clave.encode("ascii"))  # no lanza: es una clave válida
    assert "PRISMA_CLAVE_CREDENCIALES" in salida
    assert "recifrar" in salida
    assert "disponible más adelante" not in salida
    # No escribe ningún archivo.
    assert list(tmp_path.iterdir()) == []


def test_google_clave_nueva_genera_una_clave_distinta_cada_vez(capsys):
    def una() -> str:
        cli.main(["google", "clave-nueva"])
        salida = capsys.readouterr().out
        return _linea_clave(salida)
    assert una() != una()
