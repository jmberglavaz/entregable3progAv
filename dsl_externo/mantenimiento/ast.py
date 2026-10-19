from dataclasses import dataclass, field
from decimal import Decimal
from typing import Optional, List
from dominio.modelos import Condicion

"""
Puntos congelados:
En ActualizarProducto, None significa “no especificado”; no usen None para “categoría vacía” en el AST. Para vaciar categoría, el DSL debe poder representar "".
En ActualizarPromocion, condiciones is None significa “no reemplazar”; una lista (aunque sea vacía) significa “reemplazar todas las condiciones”.
El operador en Condicion.operador es exactamente "=" o ">=".
"""

@dataclass
class AgregarProducto:
    codigo: int
    nombre: Optional[str] = None
    precio: Optional[Decimal] = None
    categoria: Optional[str] = None

@dataclass
class ActualizarProducto:
    codigo: int
    nombre: Optional[str] = None
    precio: Optional[Decimal] = None
    categoria: Optional[str] = None

@dataclass
class EliminarProducto:
    codigo: int

@dataclass
class AgregarPromocion:
    codigo: int
    nombre: Optional[str] = None
    descuento: Optional[Decimal] = None
    condiciones: Optional[List[Condicion]] = None

@dataclass
class ActualizarPromocion:
    codigo: int
    nombre: Optional[str] = None
    descuento: Optional[Decimal] = None
    condiciones: Optional[List[Condicion]] = None

@dataclass
class EliminarPromocion:
    codigo: int

ComandoMantenimiento = (
    AgregarProducto | ActualizarProducto | EliminarProducto |
    AgregarPromocion | ActualizarPromocion | EliminarPromocion
)