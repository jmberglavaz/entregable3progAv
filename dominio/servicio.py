from decimal import Decimal
from typing import Optional, List, Tuple, Any
from .modelos import Producto, Promocion, Compra, Condicion, NO_CAMBIAR, OPERADOR_IGUAL, OPERADOR_MAYOR_IGUAL
from .errores import ErrorSemantico
from .motor_compras import Motor_Compras

class SupermercadoService:
    def __init__(self):
        # Usamos diccionarios para búsquedas rápidas por código
        self._productos: dict[int, Producto] = {}
        self._promociones: dict[int, Promocion] = {}
        self._compras: List[Compra] = []

    # --- VALIDACIONES AUXILIARES ---
    def _validar_texto(self, texto: str, campo: str):
        if not isinstance(texto, str) or not texto.strip():
            raise ErrorSemantico(f"El campo {campo} debe ser un texto válido.")

    def _validar_decimal(self, valor: Decimal, campo: str):
        if not isinstance(valor, Decimal) or valor < 0:
            raise ErrorSemantico(f"El campo {campo} debe ser un número positivo.")
        # Validar hasta 2 decimales
        if valor.as_tuple().exponent < -2:
            raise ErrorSemantico(f"El campo {campo} no puede tener más de 2 decimales.")

    def _validar_entero(self, valor: int, campo: str):
        if not isinstance(valor, int) or valor < 0:
            raise ErrorSemantico(f"El campo {campo} debe ser un entero positivo.")

    # --- PRODUCTOS ---
    def agregar_producto(self, codigo: int, nombre: str, precio: Decimal, categoria: Optional[str] = None) -> None:
        self._validar_entero(codigo, "código")
        if codigo in self._productos:
            raise ErrorSemantico(f"El producto con código {codigo} ya existe.")
        
        self._validar_texto(nombre, "nombre")
        self._validar_decimal(precio, "precio")
        if categoria:
            self._validar_texto(categoria, "categoría")
            
        self._productos[codigo] = Producto(codigo, nombre, precio, categoria)

    def actualizar_producto(self, codigo: int, nombre=NO_CAMBIAR, precio=NO_CAMBIAR, categoria=NO_CAMBIAR) -> None:
        if codigo not in self._productos:
            raise ErrorSemantico(f"El producto con código {codigo} no existe.")
            
        if nombre is not NO_CAMBIAR:
            self._validar_texto(nombre, "nombre")
            self._productos[codigo].nombre = nombre
            
        if precio is not NO_CAMBIAR:
            self._validar_decimal(precio, "precio")
            self._productos[codigo].precio = precio
            
        if categoria is not NO_CAMBIAR:
            if categoria: self._validar_texto(categoria, "categoría")
            self._productos[codigo].categoria = categoria

    def eliminar_producto(self, codigo: int) -> None:
        if codigo not in self._productos:
            raise ErrorSemantico(f"El producto {codigo} no existe.")
        
        for promo in self._promociones.values():
            for cond in promo.condiciones:
                if cond.codigo_producto == codigo:
                    raise ErrorSemantico(f"No se puede eliminar el producto {codigo} porque está en la promoción {promo.codigo}.")
                    
        del self._productos[codigo]

    # --- PROMOCIONES ---
    def _validar_condiciones(self, condiciones: List[Condicion]):
        if not condiciones:
            raise ErrorSemantico("La promoción debe tener al menos una condición.")
        
        codigos_vistos = set()
        for cond in condiciones:
            if cond.codigo_producto not in self._productos:
                raise ErrorSemantico(f"El producto {cond.codigo_producto} asociado a la promoción no existe.")
            if cond.codigo_producto in codigos_vistos:
                raise ErrorSemantico(f"No puede haber más de una condición para el producto {cond.codigo_producto}.")
            codigos_vistos.add(cond.codigo_producto)

    def agregar_promocion(self, codigo: int, nombre: str, descuento: Decimal, condiciones: List[Condicion]) -> None:
        self._validar_entero(codigo, "código")
        if codigo in self._promociones:
            raise ErrorSemantico(f"La promoción con código {codigo} ya existe.")
            
        self._validar_texto(nombre, "nombre")
        self._validar_decimal(descuento, "descuento")
        self._validar_condiciones(condiciones)
        
        self._promociones[codigo] = Promocion(codigo, nombre, descuento, condiciones)

    def actualizar_promocion(self, codigo: int, nombre=NO_CAMBIAR, descuento=NO_CAMBIAR, condiciones=NO_CAMBIAR) -> None:
        if codigo not in self._promociones:
            raise ErrorSemantico(f"La promoción con código {codigo} no existe.")
            
        if nombre is not NO_CAMBIAR:
            self._validar_texto(nombre, "nombre")
            self._promociones[codigo].nombre = nombre
            
        if descuento is not NO_CAMBIAR:
            self._validar_decimal(descuento, "descuento")
            self._promociones[codigo].descuento = descuento
            
        if condiciones is not NO_CAMBIAR:
            self._validar_condiciones(condiciones)
            self._promociones[codigo].condiciones = condiciones

    def eliminar_promocion(self, codigo: int) -> None:
        if codigo not in self._promociones:
            raise ErrorSemantico(f"La promoción con código {codigo} no existe.")
        del self._promociones[codigo]

    # --- COMPRAS ---
    def realizar_compra(self, items: List[Tuple[int, int]]) -> Compra:
        if not items:
            raise ErrorSemantico("La compra debe tener al menos un producto.")
            
        # El profe pidió agrupar productos repetidos ANTES de aplicar promociones
        items_agrupados = {}
        for cod, cant in items:
            if cod not in self._productos:
                raise ErrorSemantico(f"El producto con código {cod} no existe.")
            self._validar_entero(cant, f"cantidad del producto {cod}")
            items_agrupados[cod] = items_agrupados.get(cod, 0) + cant
            
        # Convertimos a lista de tuplas para el motor
        items_finales = list(items_agrupados.items())
        
        # Instanciamos el motor pasándole listas
        motor = Motor_Compras(list(self._productos.values()), list(self._promociones.values()))
        compra = motor.aplicar(items_finales)
        
        self._compras.append(compra)
        return compra

    # --- LISTADOS ---
    def listar_productos(self) -> List[Producto]:
        return list(self._productos.values())

    def listar_promociones(self) -> List[Promocion]:
        return list(self._promociones.values())
        
    def listar_compras(self) -> List[Compra]:
        return self._compras