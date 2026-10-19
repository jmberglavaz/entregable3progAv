from dataclasses import dataclass, field
from decimal import Decimal
from typing import Optional, List

@dataclass
class Producto:
    codigo: int
    nombre: str
    precio: Decimal
    categoria: Optional[str] = None

@dataclass
class Condicion:
    codigo_producto: int
    operador: str          # "=" o ">="
    cantidad: int = 1

@dataclass
class Promocion:
    codigo: int
    nombre: str
    descuento: Decimal
    condiciones: List[Condicion] = field(default_factory=list)

@dataclass
class LineaCompra:
    codigo_producto: int
    nombre: str
    precio_unitario: Decimal
    cantidad: int
    porcentaje_descuento: Decimal
    importe: Decimal

@dataclass
class Compra:
    lineas: List[LineaCompra]
    promociones_aplicadas: List[int]   # códigos de promoción
    importe_total: Decimal

OPERADOR_IGUAL = "="
OPERADOR_MAYOR_IGUAL = ">="
DECIMALES_PRECIO = 2
REDONDEO = "ROUND_HALF_UP"   # usar decimal.ROUND_HALF_UP