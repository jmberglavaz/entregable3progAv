from decimal import Decimal

from dominio.modelos import Condicion, OPERADOR_IGUAL, OPERADOR_MAYOR_IGUAL
from dominio.servicio import SupermercadoService


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
        if self._builder_pendiente is not None:
            self._builder_pendiente.commit()
            self._builder_pendiente = None


class ProductoBuilder:
    def __init__(self, dsl: DSLSupermercado, codigo: int):
        self.dsl = dsl
        self.codigo = codigo
        self._nombre = None
        self._precio = None
        self._categoria = None

    def nombre(self, nombre: str) -> "ProductoBuilder":
        self._nombre = nombre
        return self

    def precio(self, precio) -> "ProductoBuilder":
        self._precio = Decimal(str(precio))
        return self

    def categoria(self, categoria: str) -> "ProductoBuilder":
        self._categoria = categoria
        return self

    def producto(self, codigo: int) -> "ProductoBuilder":
        return self.dsl.producto(codigo)

    def promocion(self, codigo: int) -> "PromocionBuilder":
        return self.dsl.promocion(codigo)

    def finalizar(self) -> None:
        self.dsl.finalizar()

    def commit(self):
        if self._nombre is not None and self._precio is not None:
            self.dsl.service.agregar_producto(
                codigo=self.codigo,
                nombre=self._nombre,
                precio=self._precio,
                categoria=self._categoria,
            )


class PromocionBuilder:
    def __init__(self, dsl: DSLSupermercado, codigo: int):
        self.dsl = dsl
        self.codigo = codigo
        self._nombre = None
        self._descuento = Decimal("0")
        self.condiciones = []

    def nombre(self, nombre: str) -> "PromocionBuilder":
        self._nombre = nombre
        return self

    def descuento(self, porcentaje) -> "PromocionBuilder":
        self._descuento = Decimal(str(porcentaje))
        return self

    def cuando_producto(self, codigo: int) -> "CondicionBuilder":
        condicion = Condicion(
            codigo_producto=codigo,
            operador=OPERADOR_IGUAL,
            cantidad=1,
        )
        self.condiciones.append(condicion)
        return CondicionBuilder(self, condicion)

    def producto(self, codigo: int) -> "ProductoBuilder":
        return self.dsl.producto(codigo)

    def promocion(self, codigo: int) -> "PromocionBuilder":
        return self.dsl.promocion(codigo)

    def finalizar(self) -> None:
        self.dsl.finalizar()

    def commit(self):
        if self._nombre is not None and self._descuento > 0 and self.condiciones:
            self.dsl.service.agregar_promocion(
                codigo=self.codigo,
                nombre=self._nombre,
                descuento=self._descuento,
                condiciones=self.condiciones,
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