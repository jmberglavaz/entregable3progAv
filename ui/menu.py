from dsl_externo.compras.ejecutor import ejecutar_compras
from dsl_externo.compras.parser import parse_compras
from dsl_externo.mantenimiento.ejecutor import ejecutar_mantenimiento
from dsl_externo.mantenimiento.parser import parse_mantenimiento
from dominio.errores import ErrorSintactico


MENU = """
=== Supermercado ===
1. Mantenimiento de productos y promociones
2. Realizar compras
3. Ver lista de productos
4. Ver lista de promociones
5. Ver lista de compras
0. Salir
"""


def ejecutar_menu(service, input_fn=input, print_fn=print):
    while True:
        print_fn(MENU)
        opcion = input_fn("Opción: ").strip()
        if opcion == "0":
            print_fn("Chau.")
            return
        elif opcion == "1":
            _mantenimiento(service, input_fn, print_fn)
        elif opcion == "2":
            _compras(service, input_fn, print_fn)
        elif opcion == "3":
            imprimir_productos(service.listar_productos(), print_fn)
        elif opcion == "4":
            imprimir_promociones(
                service.listar_promociones(),
                service.listar_productos(),
                print_fn,
            )
        elif opcion == "5":
            imprimir_compras(service.listar_compras(), print_fn)
        else:
            print_fn(f"Opción inválida: {opcion!r}")


def _mantenimiento(service, input_fn, print_fn):
    ruta = input_fn("Ruta del archivo de mantenimiento: ").strip()
    try:
        texto = _leer(ruta)
    except FileNotFoundError:
        print_fn(f"No se encontró el archivo: {ruta}")
        return
    try:
        comandos = parse_mantenimiento(texto)
    except ErrorSintactico as e:
        print_fn(f"Error sintáctico: {e.mensaje}")
        return
    errores = ejecutar_mantenimiento(comandos, service)
    if errores:
        print_fn(f"{len(errores)} error(es) semántico(s):")
        for e in errores:
            print_fn(f"  - {e.mensaje}")
    else:
        print_fn(f"{len(comandos)} comando(s) ejecutado(s) sin errores.")


def _compras(service, input_fn, print_fn):
    ruta = input_fn("Ruta del archivo de compras: ").strip()
    try:
        texto = _leer(ruta)
    except FileNotFoundError:
        print_fn(f"No se encontró el archivo: {ruta}")
        return
    try:
        comandos = parse_compras(texto)
    except ErrorSintactico as e:
        print_fn(f"Error sintáctico: {e.mensaje}")
        return
    compras, errores = ejecutar_compras(comandos, service)
    if compras:
        print_fn(f"{len(compras)} compra(s) realizada(s):")
        imprimir_compras(compras, print_fn)
    if errores:
        print_fn(f"{len(errores)} error(es) semántico(s):")
        for e in errores:
            print_fn(f"  - {e.mensaje}")


def _leer(ruta):
    with open(ruta, encoding="utf-8") as f:
        return f.read()


# --- Impresión (funciones puras: reciben datos, no el service) ---

def imprimir_productos(productos, print_fn=print):
    if not productos:
        print_fn("(sin productos)")
        return
    print_fn("=== Productos ===")
    for p in productos:
        cat = p.categoria if p.categoria else "(sin categoría)"
        print_fn(f"{p.codigo:>4} | {p.nombre:<20} | {p.precio:>8} | {cat}")


def imprimir_promociones(promociones, productos, print_fn=print):
    if not promociones:
        print_fn("(sin promociones)")
        return
    nombres = {p.codigo: p.nombre for p in productos}
    print_fn("=== Promociones ===")
    for pr in promociones:
        print_fn(f"{pr.codigo:>4} | {pr.nombre:<20} | {pr.descuento:>5}%")
        for c in pr.condiciones:
            nombre = nombres.get(c.codigo_producto, "(desconocido)")
            print_fn(
                f"       - producto {c.codigo_producto} ({nombre}) "
                f"{c.operador} {c.cantidad}"
            )


def imprimir_compras(compras, print_fn=print):
    if not compras:
        print_fn("(sin compras)")
        return
    print_fn("=== Compras ===")
    for i, c in enumerate(compras, 1):
        print_fn(f"Compra #{i}")
        for l in c.lineas:
            print_fn(
                f"  {l.codigo_producto:>4} | {l.nombre:<20} | "
                f"{l.cantidad} x {l.precio_unitario} | "
                f"{l.porcentaje_descuento}% | {l.importe}"
            )
        print_fn(f"  Promociones aplicadas: {c.promociones_aplicadas}")
        print_fn(f"  TOTAL: {c.importe_total}")