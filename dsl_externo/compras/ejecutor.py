from typing import List, Tuple
from dominio.servicio import SupermercadoService
from dominio.errores import ErrorSemantico
from dominio.modelos import Compra

def ejecutar_compras(
    comandos: List[CompraCommand],
    service: SupermercadoService,
) -> Tuple[List[Compra], List[ErrorSemantico]]: ...