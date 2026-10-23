from decimal import Decimal

import pytest

from dominio.errores import ErrorSemantico
from tests.fakes import FakeServicePoblado
from ui.menu import (
    ejecutar_menu, imprimir_compras, imprimir_productos, imprimir_promociones,
)


def _inputs(*valores):
    it = iter(valores)
    return lambda _prompt="": next(it)


def _capturar():
    out = []
    return out, lambda s: out.append(s)


def _texto(out):
    return "\n".join(out)


# --- Flujo básico ---

def test_salir():
    out, pr = _capturar()
    ejecutar_menu(FakeServicePoblado(), input_fn=_inputs("0"), print_fn=pr)
    assert "Saludos!" in out


def test_opcion_invalida():
    out, pr = _capturar()
    ejecutar_menu(FakeServicePoblado(),
                  input_fn=_inputs("x", "0"), print_fn=pr)
    assert any("Opción inválida" in s for s in out)


# --- Impresión directa ---

def test_imprimir_productos_muestra_campos():
    out, pr = _capturar()
    imprimir_productos(FakeServicePoblado().listar_productos(), pr)
    texto = _texto(out)
    assert "Harina" in texto
    assert "Bebida" in texto


def test_imprimir_productos_vacio():
    out, pr = _capturar()
    imprimir_productos([], pr)
    assert "(sin productos)" in out


def test_imprimir_promociones_incluye_nombre_producto():
    fake = FakeServicePoblado()
    out, pr = _capturar()
    imprimir_promociones(
        fake.listar_promociones(), fake.listar_productos(), pr,
    )
    texto = _texto(out)
    assert "Harina x5" in texto
    assert "Harina" in texto      # nombre resuelto
    assert ">=" in texto
    assert "5" in texto


def test_imprimir_compras_muestra_lineas_y_total():
    out, pr = _capturar()
    imprimir_compras(FakeServicePoblado().listar_compras(), pr)
    texto = _texto(out)
    assert "Compra #1" in texto
    assert "Harina" in texto
    assert "20%" in texto
    assert "120" in texto
    assert "Promociones aplicadas" in texto


# --- Ver desde el menú ---

def test_menu_ver_productos():
    out, pr = _capturar()
    ejecutar_menu(FakeServicePoblado(),
                  input_fn=_inputs("3", "0"), print_fn=pr)
    assert "=== Productos ===" in _texto(out)


def test_menu_ver_promociones():
    out, pr = _capturar()
    ejecutar_menu(FakeServicePoblado(),
                  input_fn=_inputs("4", "0"), print_fn=pr)
    assert "=== Promociones ===" in _texto(out)
    assert "Harina" in _texto(out)


def test_menu_ver_compras():
    out, pr = _capturar()
    ejecutar_menu(FakeServicePoblado(),
                  input_fn=_inputs("5", "0"), print_fn=pr)
    assert "=== Compras ===" in _texto(out)


# --- Mantenimiento ---

def test_mantenimiento_archivo_inexistente():
    out, pr = _capturar()
    ejecutar_menu(FakeServicePoblado(),
                  input_fn=_inputs("1", "/no/existe.dsl", "0"),
                  print_fn=pr)
    assert any("No se encontró" in s for s in out)


def test_mantenimiento_error_sintactico():
    out, pr = _capturar()
    ejecutar_menu(FakeServicePoblado(),
                  input_fn=_inputs(
                      "1", "tests/fixtures/mantenimiento_invalido_sintaxis.dsl", "0"),
                  print_fn=pr)
    assert any("Error sintáctico" in s for s in out)


def test_mantenimiento_valido_sin_errores():
    out, pr = _capturar()
    ejecutar_menu(FakeServicePoblado(),
                  input_fn=_inputs(
                      "1", "tests/fixtures/mantenimiento_valido.dsl", "0"),
                  print_fn=pr)
    assert any("sin errores" in s for s in out)


def test_mantenimiento_con_errores_semanticos():
    fake = FakeServicePoblado()
    fake.errores_programados[("agregar_producto", 5)] = ErrorSemantico("dup")
    out, pr = _capturar()
    ejecutar_menu(fake,
                  input_fn=_inputs(
                      "1", "tests/fixtures/mantenimiento_valido.dsl", "0"),
                  print_fn=pr)
    texto = _texto(out)
    assert "error(es) semántico" in texto
    assert "dup" in texto


# --- Compras ---

def test_compras_archivo_inexistente():
    out, pr = _capturar()
    ejecutar_menu(FakeServicePoblado(),
                  input_fn=_inputs("2", "/no/existe.dsl", "0"),
                  print_fn=pr)
    assert any("No se encontró" in s for s in out)


def test_compras_error_sintactico():
    out, pr = _capturar()
    ejecutar_menu(FakeServicePoblado(),
                  input_fn=_inputs(
                      "2", "tests/fixtures/compras_invalido_sintaxis.dsl", "0"),
                  print_fn=pr)
    assert any("Error sintáctico" in s for s in out)


def test_compras_con_error_semantico():
    fake = FakeServicePoblado()
    fake.errores_programados[("realizar_compra", 2)] = ErrorSemantico("no existe")
    out, pr = _capturar()
    ejecutar_menu(fake,
                  input_fn=_inputs(
                      "2", "tests/fixtures/compras_valido.dsl", "0"),
                  print_fn=pr)
    texto = _texto(out)
    assert "error(es) semántico" in texto
    assert "no existe" in texto