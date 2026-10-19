"""
Test generalizado que verifica cada ítem de la checklist de Persona B.

Cada test lleva en el nombre el número del ítem de la checklist que verifica.
Correr con:  python3 -m pytest tests/test_checklist_juanma.py -v
"""

import ast as py_ast
import inspect
import os
import subprocess
import sys
from decimal import Decimal

import pytest

from dominio.errores import ErrorSemantico, ErrorSintactico
from dominio.modelos import Condicion

from dsl_externo.mantenimiento import ast as mant_ast
from dsl_externo.compras import ast as comp_ast
from dsl_externo.mantenimiento.parser import parse_mantenimiento
from dsl_externo.compras.parser import parse_compras
from dsl_externo.mantenimiento.ejecutor import ejecutar_mantenimiento
from dsl_externo.compras.ejecutor import ejecutar_compras

from ui.menu import (
    imprimir_compras, imprimir_productos, imprimir_promociones,
)

from tests.fakes import FakeService, FakeServicePoblado


# ---------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------

def _leer_fixture(nombre):
    ruta = os.path.join("tests", "fixtures", nombre)
    assert os.path.exists(ruta), f"Falta fixture: {ruta}"
    with open(ruta, encoding="utf-8") as f:
        return f.read()


def _capturar():
    out = []
    return out, lambda s: out.append(s)


def _imports_de(archivo):
    tree = py_ast.parse(open(archivo).read())
    nombres = []
    for node in py_ast.walk(tree):
        if isinstance(node, py_ast.Import):
            nombres.extend(a.name for a in node.names)
        elif isinstance(node, py_ast.ImportFrom):
            if node.module:
                nombres.append(node.module)
    return nombres


# ===============================================================
# Ítem 1 — ASTs completos con todos los comandos de la consigna
# ===============================================================

@pytest.mark.parametrize("nombre", [
    "AgregarProducto", "ActualizarProducto", "EliminarProducto",
    "AgregarPromocion", "ActualizarPromocion", "EliminarPromocion",
    "ComandoMantenimiento",
])
def test_1_ast_mantenimiento_tiene_comando(nombre):
    assert hasattr(mant_ast, nombre), f"Falta {nombre} en mantenimiento/ast.py"


@pytest.mark.parametrize("nombre", ["ItemCompra", "CompraCommand"])
def test_1_ast_compras_tiene_comando(nombre):
    assert hasattr(comp_ast, nombre), f"Falta {nombre} en compras/ast.py"


# ===============================================================
# Ítem 2 — Gramáticas cubren los tokens de la consigna
# ===============================================================

@pytest.mark.parametrize("texto,descripcion", [
    ('AGREGAR PRODUCTO 1 NOMBRE "x" PRECIO 10 CATEGORIA "y" FIN',
     "AGREGAR PRODUCTO con NOMBRE, PRECIO, CATEGORIA"),
    ('ACTUALIZAR PRODUCTO 2 NOMBRE "z" FIN',
     "ACTUALIZAR PRODUCTO parcial"),
    ('ELIMINAR PRODUCTO 3', "ELIMINAR PRODUCTO"),
    ('AGREGAR PROMOCION 4 NOMBRE "p" DESCUENTO 10 CUANDO PRODUCTO 5 CANTIDAD = 2 FIN',
     "AGREGAR PROMOCION con CUANDO al final y operador ="),
    ('ACTUALIZAR PROMOCION 6 CUANDO PRODUCTO 7 CANTIDAD >= 3 NOMBRE "q" FIN',
     "ACTUALIZAR PROMOCION con CUANDO al principio y operador >="),
    ('ELIMINAR PROMOCION 8', "ELIMINAR PROMOCION"),
])
def test_2_gramatica_mantenimiento_cubre_token(texto, descripcion):
    r = parse_mantenimiento(texto)
    assert len(r) == 1


@pytest.mark.parametrize("texto,descripcion", [
    ("COMPRA PRODUCTO 1 CANTIDAD 2 FIN", "COMPRA con CANTIDAD"),
    ("COMPRA PRODUCTO 1 FIN", "COMPRA sin CANTIDAD"),
    ("COMPRA PRODUCTO 1 PRODUCTO 2 CANTIDAD 3 FIN", "COMPRA multi-producto"),
])
def test_2_gramatica_compras_cubre_token(texto, descripcion):
    r = parse_compras(texto)
    assert len(r) == 1


def test_2_string_con_comillas_y_tildes():
    r = parse_mantenimiento('AGREGAR PRODUCTO 1 NOMBRE "Azúcar" PRECIO 10 FIN')
    assert r[0].nombre == "Azúcar"


def test_2_numero_con_decimales():
    r = parse_mantenimiento('AGREGAR PRODUCTO 1 NOMBRE "x" PRECIO 35.55 FIN')
    assert r[0].precio == Decimal("35.55")


# ===============================================================
# Ítem 3 — CANTIDAD opcional con default 1 en CUANDO y en COMPRA
# ===============================================================

def test_3_compra_sin_cantidad_usa_default_1():
    r = parse_compras("COMPRA PRODUCTO 5 FIN")
    assert r[0].items == [comp_ast.ItemCompra(5, 1)]


def test_3_cuando_sin_cantidad_usa_default_1_y_operador_igual():
    r = parse_mantenimiento(
        'AGREGAR PROMOCION 1 NOMBRE "p" DESCUENTO 10 CUANDO PRODUCTO 3 FIN'
    )
    assert r[0].condiciones == [Condicion(3, "=", 1)]


def test_3_cantidad_explicita_respeta_valor():
    r = parse_compras("COMPRA PRODUCTO 5 CANTIDAD 9 FIN")
    assert r[0].items[0].cantidad == 9


# ===============================================================
# Ítem 4 — CUANDO en actualización reemplaza todas las condiciones
# ===============================================================

def test_4_actualizar_sin_cuando_deja_condiciones_en_none():
    r = parse_mantenimiento('ACTUALIZAR PROMOCION 1 NOMBRE "n" FIN')
    assert r[0].condiciones is None


def test_4_actualizar_con_cuando_devuelve_lista():
    r = parse_mantenimiento(
        'ACTUALIZAR PROMOCION 1 CUANDO PRODUCTO 2 CANTIDAD >= 3 FIN'
    )
    assert r[0].condiciones == [Condicion(2, ">=", 3)]


def test_4_ejecutor_sin_cuando_no_pasa_kwarg_condiciones():
    f = FakeService()
    ejecutar_mantenimiento(
        parse_mantenimiento('ACTUALIZAR PROMOCION 1 NOMBRE "n" FIN'), f)
    kwargs = f.llamadas[0][2]
    assert "condiciones" not in kwargs


def test_4_ejecutor_con_cuando_pasa_condiciones_al_servicio():
    f = FakeService()
    ejecutar_mantenimiento(
        parse_mantenimiento(
            'ACTUALIZAR PROMOCION 1 CUANDO PRODUCTO 2 FIN'), f)
    kwargs = f.llamadas[0][2]
    assert kwargs["condiciones"] == [Condicion(2, "=", 1)]


# ===============================================================
# Ítem 5 — Parsers solo devuelven AST; no tocan el servicio
# ===============================================================

def test_5_parser_mantenimiento_no_importa_servicio():
    imports = _imports_de("dsl_externo/mantenimiento/parser.py")
    assert not any("servicio" in i.lower() for i in imports), imports


def test_5_parser_compras_no_importa_servicio():
    imports = _imports_de("dsl_externo/compras/parser.py")
    assert not any("servicio" in i.lower() for i in imports), imports


def test_5_firma_parse_mantenimiento_solo_recibe_texto():
    sig = inspect.signature(parse_mantenimiento)
    assert list(sig.parameters) == ["texto"]


def test_5_firma_parse_compras_solo_recibe_texto():
    sig = inspect.signature(parse_compras)
    assert list(sig.parameters) == ["texto"]


# ===============================================================
# Ítem 6 — Ejecutores capturan ErrorSemantico y siguen (no abortan)
# ===============================================================

def test_6_ejecutor_mantenimiento_no_aborta_y_sigue():
    f = FakeService()
    f.errores_programados[("agregar_producto", 5)] = ErrorSemantico("boom")
    cmds = parse_mantenimiento(
        'AGREGAR PRODUCTO 5 NOMBRE "a" PRECIO 10 FIN '
        'AGREGAR PRODUCTO 6 NOMBRE "b" PRECIO 20 FIN'
    )
    errs = ejecutar_mantenimiento(cmds, f)
    assert [e.mensaje for e in errs] == ["boom"]
    # El comando posterior SÍ se ejecutó
    assert f.llamadas == [("agregar_producto", 6, "b", Decimal("20"), None)]


def test_6_ejecutor_mantenimiento_acumula_multiples_errores():
    f = FakeService()
    f.errores_programados[("agregar_producto", 5)] = ErrorSemantico("e5")
    f.errores_programados[("eliminar_producto", 1)] = ErrorSemantico("e1")
    cmds = parse_mantenimiento(
        'AGREGAR PRODUCTO 5 NOMBRE "a" PRECIO 10 FIN '
        'ELIMINAR PRODUCTO 1 '
        'AGREGAR PRODUCTO 6 NOMBRE "b" PRECIO 20 FIN'
    )
    errs = ejecutar_mantenimiento(cmds, f)
    assert [e.mensaje for e in errs] == ["e5", "e1"]
    assert f.llamadas == [("agregar_producto", 6, "b", Decimal("20"), None)]


def test_6_ejecutor_compras_no_aborta_y_sigue():
    f = FakeService()
    f.errores_programados[("realizar_compra", 2)] = ErrorSemantico("no existe")
    cmds = parse_compras("COMPRA PRODUCTO 2 FIN COMPRA PRODUCTO 3 FIN")
    compras, errs = ejecutar_compras(cmds, f)
    assert len(errs) == 1
    assert len(compras) == 1
    assert len(f.llamadas) == 2


# ===============================================================
# Ítem 7 — Menú imprime productos, promociones, compras
# ===============================================================

def test_7_imprime_productos_con_codigo_nombre_precio_categoria():
    f = FakeServicePoblado()
    out, pr = _capturar()
    imprimir_productos(f.listar_productos(), pr)
    texto = "\n".join(out)
    assert "Harina" in texto
    assert "Refresco" in texto
    assert "Bebida" in texto


def test_7_imprime_promociones_con_nombre_producto_y_operador():
    f = FakeServicePoblado()
    out, pr = _capturar()
    imprimir_promociones(f.listar_promociones(), f.listar_productos(), pr)
    texto = "\n".join(out)
    # Promoción
    assert "Harina x5" in texto
    # Condición: código de producto, nombre resuelto, operador, cantidad
    assert "Harina" in texto    # nombre resuelto
    assert ">=" in texto
    assert "5" in texto


def test_7_imprime_compras_con_lineas_promos_y_total():
    f = FakeServicePoblado()
    out, pr = _capturar()
    imprimir_compras(f.listar_compras(), pr)
    texto = "\n".join(out)
    # Línea: nombre, precio, % descuento, importe
    assert "Harina" in texto
    assert "20%" in texto
    assert "120" in texto
    # Promociones aplicadas
    assert "Promociones aplicadas" in texto
    # Total
    assert "TOTAL" in texto


# ===============================================================
# Ítem 8 — Fixtures inválidos generan sintáctico o semántico según corresponda
# ===============================================================

def test_8_compras_invalido_sintaxis_lanza_ErrorSintactico():
    with pytest.raises(ErrorSintactico):
        parse_compras(_leer_fixture("compras_invalido_sintaxis.dsl"))


def test_8_mantenimiento_invalido_sintaxis_lanza_ErrorSintactico():
    with pytest.raises(ErrorSintactico):
        parse_mantenimiento(_leer_fixture("mantenimiento_invalido_sintaxis.dsl"))


def test_8_compras_invalido_semantica_parsea_ok_pero_falla_en_ejecutor():
    """
    compras_invalido_semantica.dsl es sintácticamente válido.
    El error semántico lo produce el servicio, no el parser.
    """
    if not os.path.exists("tests/fixtures/compras_invalido_semantica.dsl"):
        pytest.skip("Falta fixture compras_invalido_semantica.dsl")
    cmds = parse_compras(_leer_fixture("compras_invalido_semantica.dsl"))

    # Simulamos el servicio real: todos los productos del fixture "no existen"
    f = FakeService()
    for cmd in cmds:
        for item in cmd.items:
            f.errores_programados[("realizar_compra", item.codigo_producto)] = \
                ErrorSemantico(f"producto {item.codigo_producto} no existe")
    compras, errs = ejecutar_compras(cmds, f)
    assert errs, "El fixture debe generar al menos un error semántico"
    assert compras == []


def test_8_mantenimiento_semantico_sobre_FakeService():
    """
    Comando sintácticamente válido pero inválido a nivel de negocio
    (código duplicado, producto inexistente, etc.).
    """
    f = FakeService()
    f.errores_programados[("agregar_producto", 999)] = ErrorSemantico("código duplicado")
    cmds = parse_mantenimiento(
        'AGREGAR PRODUCTO 999 NOMBRE "x" PRECIO 10 FIN'
    )
    errs = ejecutar_mantenimiento(cmds, f)
    assert [e.mensaje for e in errs] == ["código duplicado"]


# ===============================================================
# Ítem 9 — Suite parser+ejecutor verde con FakeService
# ===============================================================

def test_9_existen_archivos_de_test_parser_y_ejecutor():
    for archivo in [
        "tests/test_parser_compras.py",
        "tests/test_parser_mantenimiento.py",
        "tests/test_ejecutor_compras.py",
        "tests/test_ejecutor_mantenimiento.py",
    ]:
        assert os.path.exists(archivo), f"Falta {archivo}"


def test_9_ejecutores_usan_FakeService():
    for archivo in [
        "tests/test_ejecutor_compras.py",
        "tests/test_ejecutor_mantenimiento.py",
    ]:
        contenido = open(archivo, encoding="utf-8").read()
        assert "FakeService" in contenido, \
            f"{archivo} no usa FakeService"


def test_9_parsers_no_usan_FakeService():
    """Los parsers no dependen del servicio ni del fake."""
    for archivo in [
        "tests/test_parser_compras.py",
        "tests/test_parser_mantenimiento.py",
    ]:
        contenido = open(archivo, encoding="utf-8").read()
        assert "FakeService" not in contenido, \
            f"{archivo} no debería importar FakeService"


def test_9_subprocess_pytest_parser_y_ejecutor_verde():
    """
    Corre en subproceso los 4 archivos de tests de parser+ejecutor
    y verifica que el exit code sea 0. Equivale al comando del checklist.
    """
    archivos = [
        "tests/test_parser_compras.py",
        "tests/test_parser_mantenimiento.py",
        "tests/test_ejecutor_compras.py",
        "tests/test_ejecutor_mantenimiento.py",
    ]
    resultado = subprocess.run(
        [sys.executable, "-m", "pytest", *archivos, "-q", "--no-header"],
        capture_output=True,
        text=True,
        cwd=os.getcwd(),
    )
    assert resultado.returncode == 0, (
        resultado.stdout + resultado.stderr
    )