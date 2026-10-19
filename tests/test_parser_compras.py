import pytest

from dominio.errores import ErrorSintactico
from dsl_externo.compras.ast import CompraCommand, ItemCompra
from dsl_externo.compras.parser import parse_compras


def test_compra_simple_con_default():
    resultado = parse_compras("COMPRA PRODUCTO 5 FIN")
    assert resultado == [
        CompraCommand(items=[ItemCompra(codigo_producto=5, cantidad=1)])
    ]


def test_compra_con_cantidad_explicita():
    resultado = parse_compras("COMPRA PRODUCTO 2 CANTIDAD 5 FIN")
    assert resultado == [
        CompraCommand(items=[ItemCompra(codigo_producto=2, cantidad=5)])
    ]


def test_compra_multiple_productos():
    resultado = parse_compras(
        "COMPRA PRODUCTO 2 CANTIDAD 5 PRODUCTO 5 PRODUCTO 3 CANTIDAD 2 FIN"
    )
    assert resultado == [
        CompraCommand(items=[
            ItemCompra(2, 5),
            ItemCompra(5, 1),
            ItemCompra(3, 2),
        ])
    ]


def test_multiples_compras_en_archivo():
    with open("tests/fixtures/compras_valido.dsl") as f:
        resultado = parse_compras(f.read())
    assert len(resultado) == 2
    assert resultado[0].items == [ItemCompra(2, 5), ItemCompra(5, 1), ItemCompra(3, 2)]
    assert resultado[1].items == [ItemCompra(3, 1), ItemCompra(4, 2)]


def test_falta_fin_es_error_sintactico():
    with pytest.raises(ErrorSintactico):
        parse_compras("COMPRA PRODUCTO 2 CANTIDAD 5")


def test_compra_sin_items_es_error_sintactico():
    with pytest.raises(ErrorSintactico):
        parse_compras("COMPRA FIN")


def test_archivo_invalido_sintaxis():
    with open("tests/fixtures/compras_invalido_sintaxis.dsl") as f:
        with pytest.raises(ErrorSintactico):
            parse_compras(f.read())