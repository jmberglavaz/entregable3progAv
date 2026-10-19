# dsl_interno/builders.py
from decimal import Decimal
from dominio.servicio import SupermercadoService
from dominio.modelos import Condicion, OPERADOR_IGUAL, OPERADOR_MAYOR_IGUAL

class DSLSupermercado:
    def __init__(self, service: SupermercadoService):
        self.service = service
        self._builder_pendiente = None  # Puede ser ProductoBuilder o PromocionBuilder

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
        """Si hay un builder en curso, lo envía al servicio."""
        if self._builder_pendiente:
            if isinstance(self._builder_pendiente, ProductoBuilder):
                self._builder_pendiente.commit()
            elif isinstance(self._builder_pendiente, PromocionBuilder):
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
        # Convertimos a Decimal. Si es un float, lo pasamos por str para evitar ruido
        self.precio = Decimal(str(precio))
        return self

    def categoria(self, categoria: str) -> "ProductoBuilder":
        self.categoria = categoria
        return self

    # Métodos para cambiar de contexto
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
        """Envía el producto al servicio (validando que tenga los datos mínimos)."""
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
        self.condiciones = []  # Lista de objetos Condicion reales

    def nombre(self, nombre: str) -> "PromocionBuilder":
        self.nombre = nombre
        return self

    def descuento(self, porcentaje) -> "PromocionBuilder":
        self.descuento = Decimal(str(porcentaje))
        return self

    def cuando_producto(self, codigo: int) -> "CondicionBuilder":
        # Creamos la condición por defecto ("=", 1) y la guardamos en la lista
        condicion = Condicion(codigo_producto=codigo, operador=OPERADOR_IGUAL, cantidad=1)
        self.condiciones.append(condicion)
        # Le pasamos la condición al CondicionBuilder para que pueda modificarla
        return CondicionBuilder(self, condicion)

    # Métodos para cambiar de contexto
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
        """Envía la promoción al servicio."""
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