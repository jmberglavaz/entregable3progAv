import streamlit as st

def mostrar_gondola():
    st.markdown("""
    <style>
    .gondola {
        background: linear-gradient(180deg, #e9c46a 0%, #d4a373 100%);
        border-radius: 16px;
        padding: 24px;
        box-shadow: inset 0 0 40px rgba(0,0,0,0.15);
    }
    .estante {
        background: #8b5e34;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
        display: flex;
        gap: 12px;
        align-items: flex-end;
        min-height: 180px;
        box-shadow: 0 4px 0 #5a3a1c;
    }
    .caja {
        background: #fefae0;
        border: 3px solid #bc6c25;
        border-radius: 10px;
        padding: 18px 24px;
        font-size: 20px;
        font-weight: 700;
        text-decoration: none !important;
        color: #283618 !important;
        display: flex;
        align-items: center;
        justify-content: center;
        min-width: 200px;
        height: 120px;
        text-align: center;
        box-shadow: 4px 4px 0 #bc6c25;
        transition: transform 0.15s;
    }
    .caja:hover {
        transform: translate(-2px, -2px);
        box-shadow: 6px 6px 0 #bc6c25;
    }
    .prod {
        font-size: 56px;
        line-height: 1;
        filter: drop-shadow(2px 3px 2px rgba(0,0,0,0.3));
    }
    .titulo-gondola {
        text-align: center;
        font-size: 32px;
        font-weight: 800;
        color: #283618;
        margin-bottom: 24px;
    }
    </style>

    <div class="gondola">
      <div class="titulo-gondola">🛒 Supermercado</div>

      <div class="estante">
        <a class="caja" href="?pantalla=productos" target="_self">🛍️<br>Ver Productos</a>
        <a class="caja" href="?pantalla=promociones" target="_self">🏷️<br>Ver Promociones</a>
        <span class="prod">🍎</span>
        <span class="prod">🧀</span>
        <span class="prod">🥛</span>
      </div>

      <div class="estante">
        <span class="prod">🍷</span>
        <span class="prod">🍞</span>
        <a class="caja" href="?pantalla=mantenimiento" target="_self">✏️<br>Mantenimiento</a>
        <a class="caja" href="?pantalla=compras" target="_self">🛒<br>Comprar</a>
        <span class="prod">🥦</span>
      </div>

      <div class="estante">
        <a class="caja" href="?pantalla=historial" target="_self">📜<br>Historial</a>
        <span class="prod">🍇</span>
        <span class="prod">🥖</span>
        <span class="prod">🧃</span>
      </div>
    </div>
    """, unsafe_allow_html=True)