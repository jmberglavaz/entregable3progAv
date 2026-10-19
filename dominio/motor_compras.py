from typing import List, Tuple
from .modelos import Compra, Producto, Promocion

class ComprasEngine:
    def __init__(self, productos: List[Producto], promociones: List[Promocion]): ...

    def aplicar(
        self, items: List[Tuple[int, int]]
    ) -> Compra: ...