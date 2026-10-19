from typing import List, Tuple, Dict
from decimal import Decimal
from .modelos import (
    Compra, Producto, Promocion, LineaCompra, 
    OPERADOR_IGUAL, OPERADOR_MAYOR_IGUAL, REDONDEO, DECIMALES_PRECIO
)

class Motor_Compras:
    def __init__(self, productos: List[Producto], promociones: List[Promocion]):
        # Convertimos las listas a diccionarios para búsquedas rápidas O(1)
        self._productos: Dict[int, Producto] = {p.codigo: p for p in productos}
        self._promociones: Dict[int, Promocion] = {p.codigo: p for p in promociones}

    def aplicar(self, items: List[Tuple[int, int]]) -> Compra:
        """
        items: Lista de tuplas (codigo_producto, cantidad) ya agrupada.
        Retorna un objeto Compra con las líneas, promociones e importe total.
        """
        # 1. Copia de trabajo del carrito para ir descontando stock
        carrito_trabajo = {cod: cant for cod, cant in items}
        
        # Estructura para guardar los descuentos aplicados a cada unidad.
        # Llave: codigo_producto, Valor: lista de porcentajes de descuento.
        descuentos_por_unidad: Dict[int, List[Decimal]] = {cod: [] for cod in carrito_trabajo}
        
        promociones_aplicadas_codigos = []
        
        # 2. Bucle Greedy: buscar la mejor promoción aplicable iterativamente
        while True:
            mejor_promo = None
            mejor_consumo = None 
            mejor_descuento = Decimal('-1.0')
            mejor_prioridad = -1 # Criterio de desempate (cantidad de unidades)
            
            """
            Desempate: Si dos promociones dan el mismo porcentaje de descuento, gana la que consuma más unidades 
            (esto ayuda a que el motor siempre llegue al mismo resultado y no dependa del orden de los diccionarios).
            """

            for promo in self._promociones.values():
                consumo = self._evaluar_promocion(promo, carrito_trabajo)
                
                if consumo is not None:
                    # Es aplicable. ¿Es mejor que la actual?
                    if promo.descuento > mejor_descuento:
                        mejor_promo = promo
                        mejor_consumo = consumo
                        mejor_descuento = promo.descuento
                        mejor_prioridad = sum(consumo.values())
                    elif promo.descuento == mejor_descuento:
                        # Desempate: la que consuma más unidades
                        prioridad = sum(consumo.values())
                        if prioridad > mejor_prioridad:
                            mejor_promo = promo
                            mejor_consumo = consumo
                            mejor_prioridad = prioridad

            if mejor_promo is None:
                # No se puede aplicar ninguna promoción más
                break

            # Aplicar la mejor promoción encontrada
            promociones_aplicadas_codigos.append(mejor_promo.codigo)
            
            for cod, cant in mejor_consumo.items():
                for _ in range(cant):
                    descuentos_por_unidad[cod].append(mejor_promo.descuento)
                carrito_trabajo[cod] -= cant

        # 3. Construir las líneas de compra
        lineas = []
        importe_total = Decimal('0.0')
        
        # Mapeo para llevar el control de qué productos ya procesamos
        # (por si un producto estaba en el carrito original pero se consumió todo)
        for cod, cant_original in items:
            if cod not in descuentos_por_unidad:
                continue # Ya fue procesado (no debería pasar por cómo armamos el dict)
                
            prod = self._productos[cod]
            lista_dsctos = descuentos_por_unidad[cod]
            
            # Rellenar con 0.0 las unidades que no recibieron descuento
            while len(lista_dsctos) < cant_original:
                lista_dsctos.append(Decimal('0.0'))
                
            # Calcular el importe de la línea
            precio_unitario = prod.precio
            importe_sin_dscto = precio_unitario * cant_original
            
            # Sumamos el descuento en dinero de cada unidad
            importe_dscto_total = sum(
                (precio_unitario * (d / Decimal('100'))) for d in lista_dsctos
            )
            
            importe_linea = (importe_sin_dscto - importe_dscto_total).quantize(
                Decimal(f'1.{"0" * DECIMALES_PRECIO}'), rounding=REDONDEO
            )
            
            # Calcular el porcentaje de descuento efectivo de la línea
            if importe_sin_dscto > 0:
                dscto_efectivo = (importe_dscto_total / importe_sin_dscto) * Decimal('100')
            else:
                dscto_efectivo = Decimal('0.0')
                
            linea = LineaCompra(
                codigo_producto=cod,
                nombre=prod.nombre,
                precio_unitario=precio_unitario,
                cantidad=cant_original,
                porcentaje_descuento=dscto_efectivo.quantize(Decimal('0.01'), rounding=REDONDEO),
                importe=importe_linea
            )
            lineas.append(linea)
            importe_total += importe_linea

        return Compra(
            lineas=lineas,
            promociones_aplicadas=promociones_aplicadas_codigos,
            importe_total=importe_total
        )

    def _evaluar_promocion(self, promo: Promocion, carrito_trabajo: Dict[int, int]) -> Dict[int, int] | None:
        """
        Si la promoción se puede aplicar, retorna un dict con {cod_producto: cantidad_a_consumir}.
        Si no, retorna None.
        """
        consumo = {}
        for cond in promo.condiciones:
            stock = carrito_trabajo.get(cond.codigo_producto, 0)
            
            if cond.operador == OPERADOR_IGUAL:
                if stock < cond.cantidad:
                    return None
                consumo[cond.codigo_producto] = cond.cantidad
            elif cond.operador == OPERADOR_MAYOR_IGUAL:
                if stock < cond.cantidad:
                    return None
                # Si es >=, consume exactamente la cantidad mínima requerida
                consumo[cond.codigo_producto] = cond.cantidad
                
        return consumo