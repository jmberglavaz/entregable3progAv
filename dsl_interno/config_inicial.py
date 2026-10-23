from dominio.servicio import SupermercadoService
from .builders import DSLSupermercado

def cargar_configuracion_inicial(service: SupermercadoService) -> None:
    """
    Realiza la carga inicial del supermercado utilizando el DSL interno.
    Basado en el ejemplo de la página 4 de la letra.
    """
    dsl = DSLSupermercado(service)
    
    (dsl
        # --- PRODUCTOS ---
        .producto(1)
            .nombre("Arroz")
            .precio(50)
            .categoria("Comestible")
        .producto(2)
            .nombre("Harina")
            .precio(30)
            # Sin categoría (es opcional)
        .producto(3)
            .categoria("Bebida")
            .precio(100)
            .nombre("Refresco")
        .producto(4)
            .precio(150)
            .nombre("Pizza")
            
        # --- PROMOCIONES ---
        .promocion(1)
            .nombre("Harina x5")
            .cuando_producto(2).cantidad_mayor_igual(5)
            .descuento(20)
        .promocion(2)
            .descuento(25)
            .cuando_producto(3).cantidad_igual(1)
            .cuando_producto(4).cantidad_igual(2)
            .nombre("2 pizzas + refresco")
            
        # --- CIERRE ---
        .finalizar()
    )