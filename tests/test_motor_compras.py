import pytest
from decimal import Decimal
from dominio.modelos import Producto, Promocion, Condicion, OPERADOR_IGUAL, OPERADOR_MAYOR_IGUAL
from dominio.motor_compras import Motor_Compras

@pytest.fixture
def setup_motor():
    # Productos base
    p1 = Producto(1, "Harina", Decimal('10.00'))
    p2 = Producto(2, "Levadura", Decimal('5.00'))
    p3 = Producto(3, "Azúcar", Decimal('8.00'))
    productos = [p1, p2, p3]

    # Promociones de la letra
    # P1: 1 Harina + 1 Levadura, 30%
    cond1 = [Condicion(1, OPERADOR_IGUAL, 1), Condicion(2, OPERADOR_IGUAL, 1)]
    promo1 = Promocion(1, "P1", Decimal('30'), cond1)

    # P2: 2 Harina + 1 Azúcar, 20%
    cond2 = [Condicion(1, OPERADOR_IGUAL, 2), Condicion(3, OPERADOR_IGUAL, 1)]
    promo2 = Promocion(2, "P2", Decimal('20'), cond2)

    # P3: 4 Harinas, 10%
    cond3 = [Condicion(1, OPERADOR_IGUAL, 4)]
    promo3 = Promocion(3, "P3", Decimal('10'), cond3)

    promociones = [promo1, promo2, promo3]
    
    return Motor_Compras(productos, promociones)

def test_compra_1(setup_motor):
    # Compra 1: 4 Harina, 1 Levadura
    # Esperado: Se aplica P1 (30%) a 1 Harina + 1 Levadura. Las otras 3 harinas no tienen descuento.
    compra = setup_motor.aplicar([(1, 4), (2, 1)])
    
    assert compra.promociones_aplicadas == [1]
    assert len(compra.lineas) == 2
    
    linea_harina = next(l for l in compra.lineas if l.codigo_producto == 1)
    assert linea_harina.cantidad == 4
    # Descuento total: 10% de 40 (P1) / 40 = 7.5% efectivo
    assert linea_harina.porcentaje_descuento == Decimal('7.50')
    # Importe: 40 - 3 = 37
    assert linea_harina.importe == Decimal('37.00')

def test_compra_2(setup_motor):
    # Compra 2: 4 Harina, 1 Levadura, 1 Azúcar
    # Esperado: P1 y P2. P1 aplica a 1 harina+levadura. P2 aplica a 2 harinas+azúcar. 1 harina sin descuento.
    compra = setup_motor.aplicar([(1, 4), (2, 1), (3, 1)])
    
    assert set(compra.promociones_aplicadas) == {1, 2}
    linea_harina = next(l for l in compra.lineas if l.codigo_producto == 1)
    # Descuentos: 1 unid al 30% (P1) y 2 unid al 20% (P2). 1 unid al 0%. Promedio: (30+40+0)/4 = 17.5%
    assert linea_harina.porcentaje_descuento == Decimal('17.50')

def test_compra_3(setup_motor):
    # Compra 3: 4 Harina
    compra = setup_motor.aplicar([(1, 4)])
    assert compra.promociones_aplicadas == [3]
    linea = compra.lineas[0]
    assert linea.porcentaje_descuento == Decimal('10.00')

def test_compra_4(setup_motor):
    # Compra 4: 1 Harina, 1 Azúcar
    compra = setup_motor.aplicar([(1, 1), (3, 1)])
    assert compra.promociones_aplicadas == []
    for linea in compra.lineas:
        assert linea.porcentaje_descuento == Decimal('0.00')

def test_compra_5(setup_motor):
    # Compra 5: 8 Harina
    # Esperado: P3 se aplica dos veces (8 harinas)
    compra = setup_motor.aplicar([(1, 8)])
    assert compra.promociones_aplicadas == [3, 3]
    linea = compra.lineas[0]
    assert linea.porcentaje_descuento == Decimal('10.00')

def test_compra_6(setup_motor):
    # Compra 6: 6 Harinas
    # Esperado: P3 se aplica una vez (4 harinas). 2 harinas sin descuento.
    compra = setup_motor.aplicar([(1, 6)])
    assert compra.promociones_aplicadas == [3]
    linea = compra.lineas[0]
    # 4 al 10%, 2 al 0%. Promedio efectivo: 40/60 = 6.67%
    assert linea.porcentaje_descuento == Decimal('6.67')