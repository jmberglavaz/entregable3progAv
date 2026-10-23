from dominio.servicio import SupermercadoService
from dsl_interno.config_inicial import cargar_configuracion_inicial
from ui.menu import ejecutar_menu


def main():
    service = SupermercadoService()
    cargar_configuracion_inicial(service)
    ejecutar_menu(service)


if __name__ == "__main__":
    main()