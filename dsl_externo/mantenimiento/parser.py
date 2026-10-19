from decimal import Decimal

from lark import Lark, Transformer
from lark.exceptions import UnexpectedInput

from dominio.errores import ErrorSintactico
from dominio.modelos import Condicion
from dsl_externo.mantenimiento.ast import (
    AgregarProducto, ActualizarProducto, EliminarProducto,
    AgregarPromocion, ActualizarPromocion, EliminarPromocion,
)


GRAMMAR = r"""
start: comando+

comando: agregar_producto
       | actualizar_producto
       | eliminar_producto
       | agregar_promocion
       | actualizar_promocion
       | eliminar_promocion

// ==== Productos ====

agregar_producto:    "AGREGAR"    "PRODUCTO" INT campo_producto* "FIN"
actualizar_producto: "ACTUALIZAR" "PRODUCTO" INT campo_producto* "FIN"
eliminar_producto:   "ELIMINAR"   "PRODUCTO" INT

campo_producto: campo_nombre_prod | campo_precio_prod | campo_categoria_prod
campo_nombre_prod:    "NOMBRE"    STRING
campo_precio_prod:    "PRECIO"    NUMBER
campo_categoria_prod: "CATEGORIA" STRING

// ==== Promociones ====

agregar_promocion:    "AGREGAR"    "PROMOCION" INT elemento_promocion* "FIN"
actualizar_promocion: "ACTUALIZAR" "PROMOCION" INT elemento_promocion* "FIN"
eliminar_promocion:   "ELIMINAR"   "PROMOCION" INT

elemento_promocion: campo_nombre_promo | campo_descuento_promo | bloque_cuando
campo_nombre_promo:    "NOMBRE"    STRING
campo_descuento_promo: "DESCUENTO" NUMBER

bloque_cuando: "CUANDO" condicion+
condicion: "PRODUCTO" INT ("CANTIDAD" OPERADOR INT)?

// ==== Terminales ====

OPERADOR: ">=" | "="
NUMBER: /\d+(\.\d{1,2})?/
INT: /\d+/
STRING: /"[^"]*"/

%import common.WS
%ignore WS
"""

class _MantenimientoTransformer(Transformer):

    # --- Terminales ---
    def INT(self, tok):
        return int(tok)

    def NUMBER(self, tok):
        return Decimal(str(tok))

    def STRING(self, tok):
        return str(tok)[1:-1]   # quita comillas

    def OPERADOR(self, tok):
        return str(tok)         # ">=" o "="

    # --- Productos ---
    def campo_nombre_prod(self, children):
        return ("nombre", children[0])

    def campo_precio_prod(self, children):
        return ("precio", children[0])

    def campo_categoria_prod(self, children):
        return ("categoria", children[0])

    def campo_producto(self, children):
        return children[0]

    def agregar_producto(self, children):
        codigo = children[0]
        campos = dict(children[1:])
        return AgregarProducto(
            codigo=codigo,
            nombre=campos.get("nombre"),
            precio=campos.get("precio"),
            categoria=campos.get("categoria"),
        )

    def actualizar_producto(self, children):
        codigo = children[0]
        campos = dict(children[1:])
        return ActualizarProducto(
            codigo=codigo,
            nombre=campos.get("nombre"),
            precio=campos.get("precio"),
            categoria=campos.get("categoria"),
        )

    def eliminar_producto(self, children):
        return EliminarProducto(codigo=children[0])

    # --- Promociones ---
    def campo_nombre_promo(self, children):
        return ("nombre", children[0])

    def campo_descuento_promo(self, children):
        return ("descuento", children[0])

    def elemento_promocion(self, children):
        return children[0]

    def condicion(self, children):
        codigo = children[0]
        if len(children) == 1:
            return Condicion(codigo_producto=codigo, operador="=", cantidad=1)
        return Condicion(
            codigo_producto=codigo,
            operador=children[1],
            cantidad=children[2],
        )

    def bloque_cuando(self, children):
        return ("condiciones", list(children))

    def agregar_promocion(self, children):
        codigo = children[0]
        campos = dict(children[1:])
        return AgregarPromocion(
            codigo=codigo,
            nombre=campos.get("nombre"),
            descuento=campos.get("descuento"),
            condiciones=campos.get("condiciones"),
        )

    def actualizar_promocion(self, children):
        codigo = children[0]
        campos = dict(children[1:])
        return ActualizarPromocion(
            codigo=codigo,
            nombre=campos.get("nombre"),
            descuento=campos.get("descuento"),
            condiciones=campos.get("condiciones"),
        )

    def eliminar_promocion(self, children):
        return EliminarPromocion(codigo=children[0])

    # --- Nivel superior ---
    def comando(self, children):
        return children[0]

    def start(self, children):
        return list(children)


_parser = Lark(GRAMMAR, parser="lalr",
               transformer=_MantenimientoTransformer())


def parse_mantenimiento(texto: str):
    try:
        return _parser.parse(texto)
    except UnexpectedInput as e:
        raise ErrorSintactico(mensaje=str(e)) from e