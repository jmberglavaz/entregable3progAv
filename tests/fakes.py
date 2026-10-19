from decimal import Decimal

from dominio.errores import ErrorSemantico
from dominio.modelos import (
    Compra, Condicion, LineaCompra, Producto, Promocion,
)


class FakeService:
    """
    Stub de SupermercadoService para tests de ejecutores.

    - Registra cada llamada en self.llamadas (lista de tuplas).
    - Permite programar errores por (metodo, codigo) en errores_programados.
    """

    def __init__(self):
        self.llamadas = []
        self.errores_programados = {}  # (metodo, codigo) -> ErrorSemantico

    # --- helper interno ---
    def _check_error(self, metodo, codigo):
        err = self.errores_programados.get((metodo, codigo))
        if err is not None:
            raise err

    # --- productos ---
    def agregar_producto(self, codigo, nombre, precio, categoria=None):
        self._check_error("agregar_producto", codigo)
        self.llamadas.append(
            ("agregar_producto", codigo, nombre, precio, categoria)
        )

    def actualizar_producto(self, codigo, **kwargs):
        self._check_error("actualizar_producto", codigo)
        self.llamadas.append(("actualizar_producto", codigo, kwargs))

    def eliminar_producto(self, codigo):
        self._check_error("eliminar_producto", codigo)
        self.llamadas.append(("eliminar_producto", codigo))

    # --- promociones ---
    def agregar_promocion(self, codigo, nombre, descuento, condiciones):
        self._check_error("agregar_promocion", codigo)
        self.llamadas.append(
            ("agregar_promocion", codigo, nombre, descuento, condiciones)
        )

    def actualizar_promocion(self, codigo, **kwargs):
        self._check_error("actualizar_promocion", codigo)
        self.llamadas.append(("actualizar_promocion", codigo, kwargs))

    def eliminar_promocion(self, codigo):
        self._check_error("eliminar_promocion", codigo)
        self.llamadas.append(("eliminar_promocion", codigo))

    # --- consultas (vacías; no se usan en estos tests) ---
    def listar_productos(self):
        return []

    def listar_promociones(self):
        return []

    def listar_compras(self):
        return []

    # --- compras ---
    def realizar_compra(self, items):
        self.llamadas.append(("realizar_compra", items))
        # Si alguno de los códigos tiene error programado, falla.
        for cod, _cant in items:
            err = self.errores_programados.get(("realizar_compra", cod))
            if err is not None:
                raise err
        return Compra(
            lineas=[],
            promociones_aplicadas=[],
            importe_total=Decimal("0"),
        )

    from dominio.modelos import (
    Compra, Condicion, LineaCompra, Producto, Promocion,
)


class FakeServicePoblado(FakeService):
    """FakeService con datos de ejemplo, para tests del menú."""

    def __init__(self):
        super().__init__()
        self._productos = [
            Producto(1, "Levadura", Decimal("20")),
            Producto(2, "Harina", Decimal("30")),
            Producto(3, "Refresco", Decimal("100"), "Bebida"),
        ]
        self._promociones = [
            Promocion(1, "Harina x5", Decimal("20"),
                      [Condicion(2, ">=", 5)]),
        ]
        self._compras = [
            Compra(
                lineas=[LineaCompra(
                    codigo_producto=2, nombre="Harina",
                    precio_unitario=Decimal("30"), cantidad=5,
                    porcentaje_descuento=Decimal("20"),
                    importe=Decimal("120"),
                )],
                promociones_aplicadas=[1],
                importe_total=Decimal("120"),
            ),
        ]

    def listar_productos(self):
        return list(self._productos)

    def listar_promociones(self):
        return list(self._promociones)

    def listar_compras(self):
        return list(self._compras)