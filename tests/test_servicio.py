# tests/test_servicio.py
import pytest
from decimal import Decimal
from dominio.servicio import SupermercadoService
from dominio.errores import ErrorSemantico
from dominio.modelos import Condicion, OPERADOR_IGUAL

@pytest.fixture
def service():
    return SupermercadoService()

def test_agregar_producto_duplicado(service):
    service.agregar_producto(1, "Arroz", Decimal('50'))
    with pytest.raises(ErrorSemantico, match="ya existe"):
        service.agregar_producto(1, "Otro", Decimal('10'))

def test_agregar_producto_sin_nombre(service):
    with pytest.raises(ErrorSemantico):
        service.agregar_producto(1, "", Decimal('50'))

def test_eliminar_producto_en_promocion(service):
    service.agregar_producto(1, "Arroz", Decimal('50'))
    service.agregar_producto(2, "Harina", Decimal('30'))
    cond = [Condicion(1, OPERADOR_IGUAL, 1)]
    service.agregar_promocion(1, "Promo", Decimal('10'), cond)
    
    with pytest.raises(ErrorSemantico, match="está en la promoción"):
        service.eliminar_producto(1)

def test_promocion_con_producto_inexistente(service):
    cond = [Condicion(99, OPERADOR_IGUAL, 1)]
    with pytest.raises(ErrorSemantico, match="no existe"):
        service.agregar_promocion(1, "Promo", Decimal('10'), cond)

def test_promocion_condicion_duplicada(service):
    service.agregar_producto(1, "Arroz", Decimal('50'))
    cond = [Condicion(1, OPERADOR_IGUAL, 1), Condicion(1, OPERADOR_IGUAL, 2)]
    with pytest.raises(ErrorSemantico, match="más de una condición"):
        service.agregar_promocion(1, "Promo", Decimal('10'), cond)

def test_compra_sin_productos(service):
    with pytest.raises(ErrorSemantico, match="al menos un producto"):
        service.realizar_compra([])

def test_compra_producto_inexistente(service):
    with pytest.raises(ErrorSemantico, match="no existe"):
        service.realizar_compra([(99, 1)])