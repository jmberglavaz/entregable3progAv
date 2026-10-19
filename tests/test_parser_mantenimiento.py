from decimal import Decimal

import pytest

from dominio.errores import ErrorSintactico
from dominio.modelos import Condicion
from dsl_externo.mantenimiento.ast import (
    AgregarProducto, ActualizarProducto, EliminarProducto,
    AgregarPromocion, ActualizarPromocion, EliminarPromocion,
)
from dsl_externo.mantenimiento.parser import parse_mantenimiento


# --- Productos ---

def test_agregar_producto_completo():
    r = parse_mantenimiento(
        'AGREGAR PRODUCTO 5 NOMBRE "Azúcar" PRECIO 60 CATEGORIA "Comestible" FIN'
    )
    assert r == [AgregarProducto(5, "Azúcar", Decimal("60"), "Comestible")]


def test_agregar_producto_orden_libre():
    r = parse_mantenimiento('AGREGAR PRODUCTO 6 PRECIO 45 NOMBRE "Leche" FIN')
    assert r == [AgregarProducto(6, "Leche", Decimal("45"), None)]


def test_agregar_producto_solo_obligatorios():
    r = parse_mantenimiento('AGREGAR PRODUCTO 7 NOMBRE "Pan" PRECIO 10 FIN')
    assert r == [AgregarProducto(7, "Pan", Decimal("10"), None)]


def test_agregar_producto_precio_con_decimales():
    r = parse_mantenimiento('AGREGAR PRODUCTO 8 NOMBRE "Yerba" PRECIO 35.55 FIN')
    assert r == [AgregarProducto(8, "Yerba", Decimal("35.55"), None)]


def test_actualizar_producto_parcial():
    r = parse_mantenimiento('ACTUALIZAR PRODUCTO 3 NOMBRE "Coca Cola" FIN')
    assert r == [ActualizarProducto(3, "Coca Cola", None, None)]


def test_actualizar_producto_dos_campos():
    r = parse_mantenimiento(
        'ACTUALIZAR PRODUCTO 2 CATEGORIA "Comestible" PRECIO 35.5 FIN'
    )
    assert r == [ActualizarProducto(2, None, Decimal("35.5"), "Comestible")]


def test_eliminar_producto():
    r = parse_mantenimiento("ELIMINAR PRODUCTO 1")
    assert r == [EliminarProducto(1)]


# --- Promociones ---

def test_actualizar_promocion_cuando_primero():
    r = parse_mantenimiento(
        'ACTUALIZAR PROMOCION 1 CUANDO PRODUCTO 2 CANTIDAD >= 3 NOMBRE "Harina x3" FIN'
    )
    assert r == [ActualizarPromocion(
        1, "Harina x3", None, [Condicion(2, ">=", 3)],
    )]


def test_agregar_promocion_cuando_ultimo():
    r = parse_mantenimiento(
        'AGREGAR PROMOCION 3 DESCUENTO 30.5 NOMBRE "Leche + Azúcar" '
        'CUANDO PRODUCTO 6 PRODUCTO 5 CANTIDAD = 1 FIN'
    )
    assert r == [AgregarPromocion(
        3, "Leche + Azúcar", Decimal("30.5"),
        [Condicion(6, "=", 1), Condicion(5, "=", 1)],
    )]


def test_eliminar_promocion():
    r = parse_mantenimiento("ELIMINAR PROMOCION 2")
    assert r == [EliminarPromocion(2)]


# --- Múltiples comandos ---

def test_archivo_valido_completo():
    with open("tests/fixtures/mantenimiento_valido.dsl") as f:
        r = parse_mantenimiento(f.read())
    assert len(r) == 8
    assert r[0] == AgregarProducto(5, "Azúcar", Decimal("60"), "Comestible")
    assert r[4] == ActualizarPromocion(
        1, "Harina x3", None, [Condicion(2, ">=", 3)],
    )
    assert r[6] == EliminarProducto(1)
    assert r[7] == EliminarPromocion(2)


# --- Errores sintácticos ---

def test_falta_fin():
    with pytest.raises(ErrorSintactico):
        parse_mantenimiento('AGREGAR PRODUCTO 5 NOMBRE "x" PRECIO 10')


def test_falta_codigo_producto():
    with pytest.raises(ErrorSintactico):
        parse_mantenimiento('AGREGAR PRODUCTO NOMBRE "Azúcar" PRECIO 60 FIN')


def test_precio_tres_decimales_error():
    with pytest.raises(ErrorSintactico):
        parse_mantenimiento('AGREGAR PRODUCTO 5 NOMBRE "x" PRECIO 35.555 FIN')


def test_codigo_con_decimal_error():
    with pytest.raises(ErrorSintactico):
        parse_mantenimiento('AGREGAR PRODUCTO 5.5 NOMBRE "x" PRECIO 10 FIN')


def test_archivo_invalido_sintaxis():
    with open("tests/fixtures/mantenimiento_invalido_sintaxis.dsl") as f:
        with pytest.raises(ErrorSintactico):
            parse_mantenimiento(f.read())