from dataclasses import dataclass, field
from typing import List

@dataclass
class ItemCompra:
    codigo_producto: int
    cantidad: int = 1

@dataclass
class CompraCommand:
    items: List[ItemCompra] = field(default_factory=list)