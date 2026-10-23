# ui/gui/pantallas/productos.py
import streamlit as st

def mostrar(service):
    if st.button("← Volver a la góndola"):
        st.query_params.clear()
        st.rerun()
    st.header("🛍️ Productos")
    prods = service.listar_productos()
    st.dataframe(
        [{"Código": p.codigo, "Nombre": p.nombre,
          "Precio": float(p.precio), "Categoría": p.categoria or ""}
         for p in prods],
        use_container_width=True,
    )