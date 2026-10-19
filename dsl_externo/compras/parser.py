from decimal import Decimal

from lark import Lark, Transformer

from dominio.errores import ErrorSintactico
from dsl_externo.compras.ast import CompraCommand, ItemCompra


GRAMMAR = r"""
start: compra+

compra: "COMPRA" item+ "FIN"

item: "PRODUCTO" INT ("CANTIDAD" INT)?

INT: /\d+/

%import common.WS
%ignore WS
"""


class _ComprasTransformer(Transformer):
    def INT(self, tok):
        return int(tok)

    def item(self, children):
        codigo = children[0]
        cantidad = children[1] if len(children) > 1 else 1
        return ItemCompra(codigo_producto=codigo, cantidad=cantidad)

    def compra(self, children):
        return CompraCommand(items=list(children))

    def start(self, children):
        return list(children)


_parser = Lark(GRAMMAR, parser="lalr", transformer=_ComprasTransformer())


def parse_compras(texto: str) -> list[CompraCommand]:
    try:
        return _parser.parse(texto)
    except Exception as e:
        # Lark lanza UnexpectedInput/UnexpectedToken/etc.
        raise ErrorSintactico(mensaje=str(e)) from e