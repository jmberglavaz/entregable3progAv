from typing import List, Tuple

from dominio.errores import ErrorSemantico
from dominio.modelos import Compra
from dominio.servicio import SupermercadoService

from dsl_externo.compras.ast import CompraCommand


def ejecutar_compras(
    comandos: List[CompraCommand],
    service: SupermercadoService,
) -> Tuple[List[Compra], List[ErrorSemantico]]:
    compras = []
    errores = []
    for cmd in comandos:
        items = [(i.codigo_producto, i.cantidad) for i in cmd.items]
        try:
            compra = service.realizar_compra(items)
            compras.append(compra)
        except ErrorSemantico as e:
            errores.append(e)
    return compras, errores