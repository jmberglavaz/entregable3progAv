from dominio.servicio import SupermercadoService

"""
Reglas congeladas:
- main.py crea el SupermercadoService, llama a cargar_configuracion_inicial(service) y luego a ejecutar_menu(service).
- Las rutas de archivos DSL se piden por consola o se usan fixtures fijas para la demo; eso lo deciden, pero el punto de entrada no cambia.
"""

def ejecutar_menu(service: SupermercadoService) -> None: ...