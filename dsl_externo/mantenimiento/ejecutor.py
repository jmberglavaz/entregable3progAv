from typing import List
from dominio.servicio import SupermercadoService
from dominio.errores import ErrorSemantico

def ejecutar_mantenimiento(
    comandos: List[ComandoMantenimiento],
    service: SupermercadoService,
) -> List[ErrorSemantico]: ...