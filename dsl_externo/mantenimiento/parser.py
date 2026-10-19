from typing import List

"""Reglas congeladas:
- parse_mantenimiento lanza ErrorSintactico si el texto no respeta la gramática.
- ejecutar_mantenimiento no lanza ErrorSemantico; los captura, sigue con el siguiente comando y devuelve la lista de errores.
- El parser no conoce SupermercadoService; el ejecutor sí.
"""

def parse_mantenimiento(texto: str) -> List[ComandoMantenimiento]: ...