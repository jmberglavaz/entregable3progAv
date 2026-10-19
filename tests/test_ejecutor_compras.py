from dominio.errores import ErrorSemantico

from dsl_externo.compras.ejecutor import ejecutar_compras
from dsl_externo.compras.parser import parse_compras
from tests.fakes import FakeService


def _run(texto, fake):
    return ejecutar_compras(parse_compras(texto), fake)


def test_compra_simple():
    fake = FakeService()
    compras, errores = _run("COMPRA PRODUCTO 2 CANTIDAD 5 FIN", fake)
    assert errores == []
    assert len(compras) == 1
    assert fake.llamadas == [("realizar_compra", [(2, 5)])]


def test_compra_multiples_productos():
    fake = FakeService()
    compras, errores = _run(
        "COMPRA PRODUCTO 2 CANTIDAD 5 PRODUCTO 5 PRODUCTO 3 CANTIDAD 2 FIN",
        fake,
    )
    assert errores == []
    assert fake.llamadas == [
        ("realizar_compra", [(2, 5), (5, 1), (3, 2)]),
    ]


def test_multiples_compras():
    fake = FakeService()
    compras, errores = _run(
        "COMPRA PRODUCTO 2 CANTIDAD 5 FIN COMPRA PRODUCTO 3 FIN",
        fake,
    )
    assert len(compras) == 2
    assert errores == []
    assert fake.llamadas == [
        ("realizar_compra", [(2, 5)]),
        ("realizar_compra", [(3, 1)]),
    ]


def test_error_semantico_no_aborta_y_registra_error():
    fake = FakeService()
    fake.errores_programados[("realizar_compra", 2)] = ErrorSemantico("no existe")
    compras, errores = _run(
        "COMPRA PRODUCTO 2 FIN COMPRA PRODUCTO 3 FIN", fake
    )
    assert len(errores) == 1
    assert errores[0].mensaje == "no existe"
    assert len(compras) == 1  # solo la del producto 3
    # Ambos intentos se registraron; el segundo además "hizo" la compra
    assert fake.llamadas == [
        ("realizar_compra", [(2, 1)]),
        ("realizar_compra", [(3, 1)]),
    ]