from decimal import Decimal

from dominio.errores import ErrorSemantico
from dominio.modelos import Condicion

from dsl_externo.mantenimiento.ejecutor import ejecutar_mantenimiento
from dsl_externo.mantenimiento.parser import parse_mantenimiento
from tests.fakes import FakeService


def _run(texto, fake):
    return ejecutar_mantenimiento(parse_mantenimiento(texto), fake)


def test_agregar_producto_completo():
    fake = FakeService()
    _run('AGREGAR PRODUCTO 5 NOMBRE "x" PRECIO 10 CATEGORIA "y" FIN', fake)
    assert fake.llamadas == [
        ("agregar_producto", 5, "x", Decimal("10"), "y"),
    ]


def test_actualizar_producto_solo_pasa_campos_presentes():
    fake = FakeService()
    _run('ACTUALIZAR PRODUCTO 3 NOMBRE "Coca Cola" FIN', fake)
    assert fake.llamadas == [
        ("actualizar_producto", 3, {"nombre": "Coca Cola"}),
    ]


def test_actualizar_producto_dos_campos():
    fake = FakeService()
    _run('ACTUALIZAR PRODUCTO 2 CATEGORIA "x" PRECIO 35.5 FIN', fake)
    assert fake.llamadas == [
        ("actualizar_producto", 2, {
            "categoria": "x",
            "precio": Decimal("35.5"),
        }),
    ]


def test_eliminar_producto():
    fake = FakeService()
    _run("ELIMINAR PRODUCTO 1", fake)
    assert fake.llamadas == [("eliminar_producto", 1)]


def test_agregar_promocion():
    fake = FakeService()
    _run(
        'AGREGAR PROMOCION 3 DESCUENTO 30 NOMBRE "p" '
        'CUANDO PRODUCTO 6 PRODUCTO 5 CANTIDAD = 1 FIN',
        fake,
    )
    assert fake.llamadas == [
        ("agregar_promocion", 3, "p", Decimal("30"),
         [Condicion(6, "=", 1), Condicion(5, "=", 1)]),
    ]


def test_actualizar_promocion_sin_cuando_no_pasa_condiciones():
    fake = FakeService()
    _run('ACTUALIZAR PROMOCION 1 NOMBRE "n" FIN', fake)
    assert fake.llamadas == [
        ("actualizar_promocion", 1, {"nombre": "n"}),
    ]


def test_actualizar_promocion_con_cuando_reemplaza():
    fake = FakeService()
    _run(
        'ACTUALIZAR PROMOCION 1 CUANDO PRODUCTO 2 CANTIDAD >= 3 NOMBRE "n" FIN',
        fake,
    )
    assert fake.llamadas == [
        ("actualizar_promocion", 1, {
            "nombre": "n",
            "condiciones": [Condicion(2, ">=", 3)],
        }),
    ]


def test_eliminar_promocion():
    fake = FakeService()
    _run("ELIMINAR PROMOCION 2", fake)
    assert fake.llamadas == [("eliminar_promocion", 2)]


def test_error_semantico_no_aborta_y_sigue():
    fake = FakeService()
    fake.errores_programados[("agregar_producto", 5)] = ErrorSemantico("dup")
    errores = _run(
        'AGREGAR PRODUCTO 5 NOMBRE "a" PRECIO 10 FIN '
        'AGREGAR PRODUCTO 6 NOMBRE "b" PRECIO 20 FIN',
        fake,
    )
    assert [e.mensaje for e in errores] == ["dup"]
    # El segundo comando sí se ejecutó
    assert fake.llamadas == [
        ("agregar_producto", 6, "b", Decimal("20"), None),
    ]


def test_multiples_errores_devueltos():
    fake = FakeService()
    fake.errores_programados[("agregar_producto", 5)] = ErrorSemantico("e5")
    fake.errores_programados[("eliminar_producto", 1)] = ErrorSemantico("e1")
    errores = _run(
        'AGREGAR PRODUCTO 5 NOMBRE "a" PRECIO 10 FIN '
        'ELIMINAR PRODUCTO 1 '
        'AGREGAR PRODUCTO 6 NOMBRE "b" PRECIO 20 FIN',
        fake,
    )
    assert [e.mensaje for e in errores] == ["e5", "e1"]
    assert fake.llamadas == [
        ("agregar_producto", 6, "b", Decimal("20"), None),
    ]