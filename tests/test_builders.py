# dsl_interno/builders.py
from decimal import Decimal
from dominio.servicio import SupermercadoService
from dominio.modelos import Condicion, OPERADOR_IGUAL, OPERADOR_MAYOR_IGUAL

class DSLSupermercado:
    def __init__(self, service: SupermercadoService):
        self.service = service
        self._builder_pendiente = None

    def producto(self, codigo: int) -> "ProductoBuilder":
        self._commit_pendiente()
        self._builder_pendiente = ProductoBuilder(self, codigo)
        return self._builder_pendiente

    def promocion(self, codigo: int) -> "PromocionBuilder":
        self._commit_pendiente()
        self._builder_pendiente = PromocionBuilder(self, codigo)
        return self._builder_pendiente

    def finalizar(self) -> None:
        self._commit_pendiente()
        return None

    def _commit_pendiente(self):
        if self._builder_pendiente:
            self._builder_pendiente.commit()
            self._builder_pendiente = None


class ProductoBuilder:
    def __init__(self, dsl: DSLSupermercado, codigo: int):
        self.dsl = dsl
        self.codigo = codigo
        self.nombre = None
        self.precio = None
        self.categoria = None

    def nombre(self, nombre: str) -> "ProductoBuilder":
        self.nombre = nombre
        return self

    def precio(self, precio) -> "ProductoBuilder":
        self.precio = Decimal(str(precio))
        return self

    def categoria(self, categoria: str) -> "ProductoBuilder":
        self.categoria = categoria
        return self

    def producto(self, codigo: int) -> "ProductoBuilder":
        self.dsl._commit_pendiente()
        return self.dsl.producto(codigo)

    def promocion(self, codigo: int) -> "PromocionBuilder":
        self.dsl._commit_pendiente()
        return self.dsl.promocion(codigo)

    def finalizar(self) -> None:
        self.dsl._commit_pendiente()
        return None

    def commit(self):
        if self.nombre is not None and self.precio is not None:
            self.dsl.service.agregar_producto(
                codigo=self.codigo,
                nombre=self.nombre,
                precio=self.precio,
                categoria=self.categoria
            )


class PromocionBuilder:
    def __init__(self, dsl: DSLSupermercado, codigo: int):
        self.dsl = dsl
        self.codigo = codigo
        self.nombre = None
        self.descuento = Decimal('0.0')
        self.condiciones = []

    def nombre(self, nombre: str) -> "PromocionBuilder":
        self.nombre = nombre
        return self

    def descuento(self, porcentaje) -> "PromocionBuilder":
        self.descuento = Decimal(str(porcentaje))
        return self

    def cuando_producto(self, codigo: int) -> "CondicionBuilder":
        condicion = Condicion(codigo_producto=codigo, operador=OPERADOR_IGUAL, cantidad=1)
        self.condiciones.append(condicion)
        return CondicionBuilder(self, condicion)

    def producto(self, codigo: int) -> "ProductoBuilder":
        self.dsl._commit_pendiente()
        return self.dsl.producto(codigo)

    def promocion(self, codigo: int) -> "PromocionBuilder":
        self.dsl._commit_pendiente()
        return self.dsl.promocion(codigo)

    def finalizar(self) -> None:
        self.dsl._commit_pendiente()
        return None

    def commit(self):
        if self.nombre is not None and self.descuento > 0 and self.condiciones:
            self.dsl.service.agregar_promocion(
                codigo=self.codigo,
                nombre=self.nombre,
                descuento=self.descuento,
                condiciones=self.condiciones
            )


class CondicionBuilder:
    def __init__(self, promo_builder: PromocionBuilder, condicion: Condicion):
        self.promo_builder = promo_builder
        self.condicion = condicion

    def cantidad_igual(self, cantidad: int) -> "PromocionBuilder":
        self.condicion.cantidad = cantidad
        self.condicion.operador = OPERADOR_IGUAL
        return self.promo_builder

    def cantidad_mayor_igual(self, cantidad: int) -> "PromocionBuilder":
        self.condicion.cantidad = cantidad
        self.condicion.operador = OPERADOR_MAYOR_IGUAL
        return self.promo_builder