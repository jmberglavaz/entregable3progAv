from decimal import Decimal
from typing import Optional, List, Tuple

"""
items es [(codigo_producto, cantidad), ...].

Reglas congeladas:
- Los métodos de mantenimiento lanzan ErrorSemantico ante error.
- NO_CAMBIAR se usa solo en actualizaciones.
- realizar_compra agrupa productos repetidos antes de aplicar promociones.
- El servicio es la única puerta de entrada al modelo.
"""
NO_CAMBIAR = object()

class SupermercadoService:
    def agregar_producto(
        self, codigo: int, nombre: str, precio: Decimal,
        categoria: Optional[str] = None
    ) -> None: ...

    def actualizar_producto(
        self, codigo: int,
        nombre=NO_CAMBIAR,
        precio=NO_CAMBIAR,
        categoria=NO_CAMBIAR,
    ) -> None: ...

    def eliminar_producto(self, codigo: int) -> None: ...

    def agregar_promocion(
        self, codigo: int, nombre: str, descuento: Decimal,
        condiciones: List[Condicion]
    ) -> None: ...

    def actualizar_promocion(
        self, codigo: int,
        nombre=NO_CAMBIAR,
        descuento=NO_CAMBIAR,
        condiciones=NO_CAMBIAR,
    ) -> None: ...

    def eliminar_promocion(self, codigo: int) -> None: ...

    def listar_productos(self) -> List[Producto]: ...
    def listar_promociones(self) -> List[Promocion]: ...
    def listar_compras(self) -> List[Compra]: ...

    def realizar_compra(self, items: List[Tuple[int, int]]) -> Compra: ...