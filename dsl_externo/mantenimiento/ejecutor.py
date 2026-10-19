from typing import List

from dominio.errores import ErrorSemantico
from dominio.servicio import SupermercadoService

from dsl_externo.mantenimiento.ast import (
    AgregarProducto, ActualizarProducto, EliminarProducto,
    AgregarPromocion, ActualizarPromocion, EliminarPromocion,
    ComandoMantenimiento,
)


def ejecutar_mantenimiento(
    comandos: List[ComandoMantenimiento],
    service: SupermercadoService,
) -> List[ErrorSemantico]:
    errores = []
    for cmd in comandos:
        try:
            _ejecutar(cmd, service)
        except ErrorSemantico as e:
            errores.append(e)
    return errores


def _ejecutar(cmd, service):
    if isinstance(cmd, AgregarProducto):
        service.agregar_producto(
            codigo=cmd.codigo,
            nombre=cmd.nombre,
            precio=cmd.precio,
            categoria=cmd.categoria,
        )
    elif isinstance(cmd, ActualizarProducto):
        kwargs = {}
        if cmd.nombre is not None:
            kwargs["nombre"] = cmd.nombre
        if cmd.precio is not None:
            kwargs["precio"] = cmd.precio
        if cmd.categoria is not None:
            kwargs["categoria"] = cmd.categoria
        service.actualizar_producto(cmd.codigo, **kwargs)
    elif isinstance(cmd, EliminarProducto):
        service.eliminar_producto(cmd.codigo)
    elif isinstance(cmd, AgregarPromocion):
        service.agregar_promocion(
            codigo=cmd.codigo,
            nombre=cmd.nombre,
            descuento=cmd.descuento,
            condiciones=cmd.condiciones,
        )
    elif isinstance(cmd, ActualizarPromocion):
        kwargs = {}
        if cmd.nombre is not None:
            kwargs["nombre"] = cmd.nombre
        if cmd.descuento is not None:
            kwargs["descuento"] = cmd.descuento
        if cmd.condiciones is not None:
            kwargs["condiciones"] = cmd.condiciones
        service.actualizar_promocion(cmd.codigo, **kwargs)
    elif isinstance(cmd, EliminarPromocion):
        service.eliminar_promocion(cmd.codigo)
    else:
        raise TypeError(f"Comando desconocido: {cmd!r}")