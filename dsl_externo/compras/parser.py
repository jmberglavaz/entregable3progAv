from typing import List

"""
Reglas congeladas:
- parse_compras lanza ErrorSintactico.
- ejecutar_compras no aborta por error semántico; devuelve compras exitosas y errores.
- El parser no conoce el servicio.
"""

def parse_compras(texto: str) -> List[CompraCommand]: ...