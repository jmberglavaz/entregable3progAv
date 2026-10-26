import streamlit as st
import textwrap

st.set_page_config(page_title="Supermercado", layout="wide")

# --- Imports con captura de errores visibles ---
try:
    from dominio.servicio import SupermercadoService
    from dsl_interno.config_inicial import cargar_configuracion_inicial
    from dsl_externo.mantenimiento.parser import parse_mantenimiento
    from dsl_externo.mantenimiento.ejecutor import ejecutar_mantenimiento
    from dsl_externo.compras.parser import parse_compras
    from dsl_externo.compras.ejecutor import ejecutar_compras
    from dominio.errores import ErrorSintactico
except Exception as e:
    st.error(f"Error de import: {e}")
    st.exception(e)
    st.stop()


# --- Servicio cacheado: sobrevive recargas de página ---
@st.cache_resource
def get_service():
    s = SupermercadoService()
    cargar_configuracion_inicial(s)
    return s

try:
    service = get_service()
except Exception as e:
    st.error(f"Error al cargar config inicial: {e}")
    st.exception(e)
    st.stop()


# --- Router por query params ---
def pantalla_actual() -> str:
    try:
        v = st.query_params.get("pantalla", "menu")
    except Exception:
        v = st.experimental_get_query_params().get("pantalla", ["menu"])[0]
    if isinstance(v, list):
        v = v[0] if v else "menu"
    return v or "menu"


def volver():
    try:
        st.query_params.clear()
    except Exception:
        st.experimental_set_query_params()
    st.rerun()


def boton_volver():
    if st.button("← Volver a la góndola", type="secondary"):
        volver()


# --- CSS global ---
st.markdown("""
<style>
.gondola {
    background: linear-gradient(180deg, #f4e4c1 0%, #e0c9a6 100%);
    border-radius: 20px;
    padding: 24px;
    box-shadow: inset 0 0 40px rgba(0,0,0,0.08);
}
.estante {
    background: linear-gradient(180deg, #a0714a 0%, #8b5e34 100%);
    border-radius: 10px;
    padding: 20px 16px 24px 16px;
    margin-bottom: 18px;
    display: flex;
    gap: 14px;
    align-items: flex-end;
    justify-content: center;
    flex-wrap: wrap;
    min-height: 170px;
    box-shadow: 0 6px 0 #5a3a1c, 0 10px 20px rgba(0,0,0,0.15);
}
.caja {
    background: #fefae0;
    border: 3px solid #bc6c25;
    border-radius: 12px;
    padding: 16px 22px;
    font-size: 16px;
    font-weight: 700;
    text-decoration: none !important;
    color: #283618 !important;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-width: 170px;
    min-height: 110px;
    text-align: center;
    box-shadow: 5px 5px 0 #bc6c25;
    transition: transform 0.12s, box-shadow 0.12s;
    gap: 6px;
    line-height: 1.2;
}
.caja:hover {
    transform: translate(-2px, -2px);
    box-shadow: 7px 7px 0 #bc6c25;
    background: #fff8d6;
}
.caja .emoji { font-size: 30px; }
.prod {
    font-size: 52px;
    line-height: 1;
    filter: drop-shadow(2px 3px 3px rgba(0,0,0,0.35));
    padding-bottom: 4px;
    transition: transform 0.2s;
}
.prod:hover { transform: scale(1.15) rotate(-3deg); }
.titulo-gondola {
    text-align: center;
    font-size: 40px;
    font-weight: 900;
    color: #283618;
    margin: 0 0 8px 0;
    text-shadow: 2px 2px 0 #fefae0;
}
.subtitulo-gondola {
    text-align: center;
    color: #5a3a1c;
    margin: 0 0 28px 0;
    font-size: 16px;
}
.caja-producto {
    background: #fefae0;
    border: 3px solid #bc6c25;
    border-radius: 12px;
    padding: 18px 20px 16px 20px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-width: 180px;
    max-width: 220px;
    min-height: 140px;
    text-align: center;
    box-shadow: 5px 5px 0 #bc6c25;
    transition: transform 0.12s, box-shadow 0.12s;
    gap: 6px;
    color: #283618;
    position: relative;
    word-break: break-word;
}
.caja-producto:hover {
    transform: translate(-2px, -2px);
    box-shadow: 7px 7px 0 #bc6c25;
    background: #fff8d6;
}
.codigo-badge {
    position: absolute;
    top: -12px;
    right: -12px;
    background: #bc6c25;
    color: #fefae0;
    font-size: 12px;
    font-weight: 800;
    padding: 3px 10px;
    border-radius: 12px;
    box-shadow: 2px 2px 0 #5a3a1c;
    letter-spacing: 0.5px;
}
.nombre-prod {
    font-size: 18px;
    font-weight: 800;
    line-height: 1.2;
    margin-bottom: 2px;
    color: #283618;
}
.precio-prod {
    font-size: 24px;
    font-weight: 900;
    color: #bc6c25;
    margin-bottom: 2px;
}
.categoria-prod {
    font-size: 11px;
    font-weight: 700;
    color: #7a5230;
    text-transform: uppercase;
    letter-spacing: 1px;
}
.estante-vacio {
    color: #5a3a1c;
    font-style: italic;
    font-weight: 600;
    padding: 60px 20px;
    text-align: center;
    font-size: 16px;
}
/* --- Estilos para los Cupones --- */
.coupon-sheet {
    display: grid;
    grid-template-columns: repeat(5, minmax(0, 1fr));
    gap: 16px;
    padding: 10px 0; /* Solo margen arriba y abajo */
    /* Le quitamos el fondo blanco y la sombra para que flote lindo */
}

.coupon {
    display: flex;
    flex-direction: column;
    border-radius: 12px;
    color: white;
    box-shadow: 4px 4px 0 rgba(0,0,0,0.15);
    position: relative;
    overflow: hidden;
    min-height: 240px; /* Le damos altura fija para que queden parejos */
    /* Mordidas laterales (simula el ticket recortable) */
    -webkit-mask-image: 
        radial-gradient(circle at 0 50%, transparent 8px, black 9px),
        radial-gradient(circle at 100% 50%, transparent 8px, black 9px);
    -webkit-mask-size: 100% 100%, 100% 100%;
    -webkit-mask-position: 0 0, 0 0;
    -webkit-mask-repeat: no-repeat, no-repeat;
}

.coupon-top {
    padding: 24px 12px 16px 12px;
    text-align: center;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    border-bottom: 2px dashed rgba(255,255,255,0.4);
    background: rgba(0,0,0,0.05);
    flex: 0 0 auto;
}

.coupon-code { 
    font-size: 12px; 
    text-transform: uppercase; 
    letter-spacing: 1.5px; 
    opacity: 0.9; 
    font-weight: 700;
}

.coupon-discount { 
    font-size: 60px; 
    font-weight: 900; 
    line-height: 1; 
    color: #ffea00; 
    text-shadow: 2px 2px 0 rgba(0,0,0,0.25); 
    margin: 8px 0; 
}

.coupon-name { 
    font-size: 20px; 
    font-weight: 800; 
    text-transform: uppercase; 
    line-height: 1.2; 
    word-break: break-word;
}

.coupon-bottom {
    padding: 20px 16px 20px 16px; /* Un toque más de aire arriba */
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}

.coupon-conditions-title { 
    text-transform: uppercase; 
    opacity: 0.9; 
    font-size: 12px; /* Subido de 9px a 12px */
    font-weight: 700; 
    margin-bottom: 10px; 
    letter-spacing: 0.5px;
}

.coupon-conditions-list { 
    margin: 0; 
    padding-left: 18px; 
    font-size: 16px; /* Tamaño solicitado */
    line-height: 1.4; 
    font-weight: 500;
}

.coupon-conditions-list b {
    font-weight: 800;
    white-space: nowrap;
}

.coupon-barcode {
    height: 32px;
    margin-top: 16px;
    background: repeating-linear-gradient(
        to right,
        #000 0, #000 2px, transparent 2px, transparent 4px,
        #000 4px, #000 5px, transparent 5px, transparent 8px,
        #000 8px, #000 10px, transparent 10px, transparent 12px
    );
    opacity: 0.85;
    border-radius: 2px;
    width: 100%;
}

/* --- Estilos para las pantallas de acción (Uploads) --- */
.action-container {
    max-width: 800px;
    margin: 0 auto;
}

.info-box {
    background-color: #f8f9fa;
    border-left: 5px solid #457b9d;
    padding: 20px;
    border-radius: 8px;
    margin-bottom: 30px;
    color: #1d3557;
    font-size: 15px;
    line-height: 1.5;
    box-shadow: 0 2px 5px rgba(0,0,0,0.05);
}
.info-box h4 {
    margin-top: 0;
    margin-bottom: 10px;
    color: #1d3557;
}
.info-box code {
    background-color: #e9ecef;
    padding: 2px 6px;
    border-radius: 4px;
    color: #e63946;
    font-weight: 700;
    font-family: monospace;
}

[data-testid="stFileUploader"] {
    width: 100%;
}
[data-testid="stFileUploader"] section {
    border: 3px dashed #bc6c25 !important;
    border-radius: 16px !important;
    background-color: #fefae0 !important;
    padding: 50px 20px !important;
    text-align: center;
    cursor: pointer;
    transition: all 0.2s ease-in-out;
    min-height: 280px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
}
[data-testid="stFileUploader"] section:hover {
    background-color: #fff8d6 !important;
    border-color: #9c5517 !important;
    transform: translateY(-2px);
}
/* Ocultar los textos y botón por defecto */
[data-testid="stFileUploader"] section > div > span,
[data-testid="stFileUploader"] section > div > small,
[data-testid="stFileUploader"] section > button {
    display: none !important;
}
/* Inyectar nuestro propio "+" y texto */
[data-testid="stFileUploader"] section::before {
    content: "+";
    font-size: 80px;
    font-weight: 300;
    color: #bc6c25;
    line-height: 1;
    margin-bottom: 10px;
}
[data-testid="stFileUploader"] section::after {
    content: "Hacé clic o arrastrá el archivo acá";
    font-size: 20px;
    font-weight: 700;
    color: #bc6c25;
}
/* Ocultar el "+" cuando ya hay un archivo subido */
[data-testid="stFileUploader"]:has([data-testid="stFileUploaderFile"]) section::before,
[data-testid="stFileUploader"]:has([data-testid="stFileUploaderFile"]) section::after {
    display: none;
}
/* Estilo para la tarjeta del archivo subido */
[data-testid="stFileUploaderFile"] {
    background-color: #fefae0 !important;
    border: 2px solid #bc6c25 !important;
    border-radius: 12px !important;
    padding: 15px !important;
    margin-top: 10px;
}
/* --- Estilos para los Tickets de Historial --- */
.receipt-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 24px;
    padding: 10px 0;
}

.receipt {
    background-color: #fbfbf8;
    color: #333;
    padding: 24px 20px;
    font-family: 'Courier New', Courier, monospace;
    box-shadow: 0 10px 20px rgba(0,0,0,0.15);
    position: relative;
    /* Efecto de borde inferior dentado */
    mask-image: linear-gradient(to bottom, black calc(100% - 10px), transparent 0),
                radial-gradient(circle at 50% 100%, transparent 5px, black 6px);
    mask-size: 100% calc(100% - 10px), 10px 10px;
    mask-repeat: no-repeat, repeat-x;
    mask-position: top left, bottom left;
    -webkit-mask-image: linear-gradient(to bottom, black calc(100% - 10px), transparent 0),
                        radial-gradient(circle at 50% 100%, transparent 5px, black 6px);
    -webkit-mask-size: 100% calc(100% - 10px), 10px 10px;
    -webkit-mask-repeat: no-repeat, repeat-x;
    -webkit-mask-position: top left, bottom left;
}

/* Efecto opcional de "sombra" arriba para que parezca que está sobre la mesa */
.receipt-wrapper {
    filter: drop-shadow(0px 5px 8px rgba(0,0,0,0.2));
}

.receipt-header {
    text-align: center;
    margin-bottom: 15px;
}

.receipt-header h2 {
    margin: 0;
    font-size: 20px;
    font-weight: 900;
    letter-spacing: 1px;
    text-transform: uppercase;
    color: #111;
}

.receipt-header p {
    margin: 4px 0 0 0;
    font-size: 12px;
    color: #666;
}

.receipt-divider {
    border-top: 1px dashed #999;
    margin: 12px 0;
}

.receipt-table {
    width: 100%;
    font-size: 15px;
    border-collapse: collapse;
    margin-bottom: 15px;
}

.receipt-table th {
    text-align: left;
    font-weight: normal;
    color: #666;
    padding-bottom: 8px;
    border-bottom: 1px solid #ddd;
}

.receipt-table td {
    padding: 8px 0;
    vertical-align: top;
}

.receipt-table td.right {
    text-align: right;
}

.receipt-table .item-name {
    display: block;
    font-weight: bold;
}

.receipt-table .item-detail {
    display: block;
    font-size: 13px;
    color: #777;
    margin-top: 2px;
}

.receipt-total-box {
    text-align: right;
    margin-top: 15px;
}

.receipt-total-box .total-label {
    font-size: 14px;
    font-weight: bold;
    text-transform: uppercase;
}

.receipt-total-box .total-amount {
    font-size: 26px;
    font-weight: 900;
    color: #000;
    margin-top: 4px;
}

.receipt-footer {
    text-align: center;
    margin-top: 20px;
    font-size: 14px;
    color: #666;
}

.receipt-barcode {
    height: 40px;
    margin: 15px auto 5px auto;
    width: 80%;
    background: repeating-linear-gradient(
        to right,
        #333 0, #333 2px, transparent 2px, transparent 4px,
        #333 4px, #333 5px, transparent 5px, transparent 9px,
        #333 9px, #333 12px, transparent 12px, transparent 14px
    );
    opacity: 0.7;
}

/* Para que el modo oscuro de Streamlit no rompa el efecto */
[data-testid="stMarkdownContainer"] .receipt-grid {
    color: #333;
}

/* --- Estilos para el botón principal --- */
div.stButton > button[kind="primary"] {
    background-color: #4f46e5 !important; /* Índigo moderno */
    color: white !important;
    border: 2px solid #4338ca !important;
    border-radius: 8px !important;
    padding: 12px 24px !important;
    font-weight: 700 !important;
    font-size: 16px !important;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
    transition: all 0.2s;
}

div.stButton > button[kind="primary"]:hover {
    background-color: #4338ca !important;
    border-color: #3730a3 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 8px -1px rgba(0, 0, 0, 0.15) !important;
}

/* --- Estilos para el botón secundario (Volver) --- */
div.stButton > button[kind="secondary"] {
    background-color: transparent !important;
    color: #a1a1aa !important;
    border: 1px solid #3f3f46 !important;
    border-radius: 8px !important;
    padding: 8px 16px !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    transition: all 0.2s;
    box-shadow: none !important;
    width: auto !important; /* Para que no ocupe todo el ancho */
}

div.stButton > button[kind="secondary"]:hover {
    background-color: #27272a !important;
    color: white !important;
    border-color: #52525b !important;
}

/* --- Estilos para el contenedor de subida --- */
/* Selecciona el contenedor de Streamlit que tiene adentro al FileUploader */
div[data-testid="stVerticalBlock"] > div:has(> div[data-testid="stFileUploader"]) {
    border: 3px dashed #bc6c25 !important;
    border-radius: 16px !important;
    background-color: #fefae0 !important;
    padding: 40px !important;
    transition: all 0.2s;
    min-height: 300px;
    display: flex;
    flex-direction: column;
    justify-content: center;
}

/* Quitar el borde nativo del uploader para que no quede doble */
[data-testid="stFileUploader"] section {
    border: none !important;
    background-color: transparent !important;
    padding: 0 !important;
    min-height: auto !important;
}
</style>
""", unsafe_allow_html=True)


# --- Pantalla: góndola ---
def pantalla_menu():
    st.markdown("""
    <div class="gondola">
      <h1 class="titulo-gondola">🛒 Supermercado</h1>
      <p class="subtitulo-gondola">Elegí una opción de la góndola</p>

      <!-- Estante 1: frutas -->
      <div class="estante">
        <span class="prod">🍎</span>
        <span class="prod">🍌</span>
        <a class="caja" href="?pantalla=productos" target="_self">
            <span class="emoji">🛍️</span>Ver Productos
        </a>
        <span class="prod">🍇</span>
        <span class="prod">🍓</span>
        <span class="prod">🥝</span>
        <span class="prod">🍑</span>
        <a class="caja" href="?pantalla=promociones" target="_self">
            <span class="emoji">🏷️</span>Ver Promociones
        </a>
        <span class="prod">🍒</span>
        <span class="prod">🥭</span>
      </div>

      <!-- Estante 2: lácteos y panadería -->
      <div class="estante">
        <span class="prod">🧀</span>
        <span class="prod">🥛</span>
        <a class="caja" href="?pantalla=mantenimiento" target="_self">
            <span class="emoji">⚙️</span>Mantenimiento
        </a>
        <span class="prod">🍞</span>
        <span class="prod">🥖</span>
        <span class="prod">🥐</span>
        <span class="prod">🧈</span>
        <a class="caja" href="?pantalla=compras" target="_self">
            <span class="emoji">🛒</span>Comprar
        </a>
        <span class="prod">🍯</span>
        <span class="prod">🥚</span>
      </div>

      <!-- Estante 3: verduras -->
      <div class="estante">
        <span class="prod">🥦</span>
        <span class="prod">🥕</span>
        <span class="prod">🥒</span>
        <span class="prod">🥬</span>
        <a class="caja" href="?pantalla=historial" target="_self">
            <span class="emoji">📜</span>Historial
        </a>
        <span class="prod">🌽</span>
        <span class="prod">🫑</span>
        <span class="prod">🧅</span>
        <span class="prod">🥔</span>
      </div>
    </div>
    """, unsafe_allow_html=True)


# --- Pantalla: productos ---
def _producto_card(p):
    """Genera el HTML de una tarjeta de producto."""
    cat = p.categoria if p.categoria else "Sin categoría"
    return f"""
    <div class="caja-producto">
        <span class="codigo-badge">#{p.codigo}</span>
        <div class="nombre-prod">{p.nombre}</div>
        <div class="precio-prod">${float(p.precio):.2f}</div>
        <div class="categoria-prod">{cat}</div>
    </div>
    """


def pantalla_productos():
    boton_volver()
    st.header("🛍️ Lista de Productos")

    prods = service.listar_productos()
    if not prods:
        st.markdown("""
        <div class="gondola">
          <h1 class="titulo-gondola">Productos</h1>
          <div class="estante"><div class="estante-vacio">No hay productos cargados.</div></div>
        </div>
        """, unsafe_allow_html=True)
        return

    # Chunkear en estantes de 4 productos
    PRODUCTOS_POR_ESTANTE = 6
    estantes = [
        prods[i:i + PRODUCTOS_POR_ESTANTE]
        for i in range(0, len(prods), PRODUCTOS_POR_ESTANTE)
    ]

    html_estantes = ""
    for estante in estantes:
        cards = "".join(_producto_card(p) for p in estante)
        html_estantes += f'<div class="estante">{cards}</div>'

    st.markdown(f"""
    <div class="gondola">
      <h1 class="titulo-gondola">Productos</h1>
      <p class="subtitulo-gondola">{len(prods)} producto(s) en stock</p>
      {html_estantes}
    </div>
    """, unsafe_allow_html=True)


# --- Pantalla: promociones ---
def pantalla_promociones():
    boton_volver()
    st.header("🏷️ Cupones de Descuento")
    
    promos = service.listar_promociones()
    nombres = {p.codigo: p.nombre for p in service.listar_productos()}
    
    if not promos:
        st.info("No hay promociones cargadas.")
        return

    # Paleta de 5 colores fijos (Rojo, Azul, Verde, Naranja, Violeta)
    COLORS = ["#e63946", "#457b9d", "#2a9d8f", "#f4a261", "#9d4edd"]
    
    html_cupones = ""
    for i, pr in enumerate(promos):
        # Lógica de colores diagonales
        row = i // 5
        col = i % 5
        color = COLORS[(row + col) % len(COLORS)]
        
        # Armar string de condiciones
        condiciones_html = ""
        for c in pr.condiciones:
            prod_nombre = nombres.get(c.codigo_producto, f"Prod {c.codigo_producto}")
            condiciones_html += f"<li>{prod_nombre} <b>{c.operador} {c.cantidad}</b></li>"
        
        if not condiciones_html:
            condiciones_html = "<li>Cualquier producto</li>"

        # IMPORTANTE: Sin indentación (espacios) al principio de las líneas
        html_cupones += f"""<div class="coupon" style="background-color: {color};">
<div class="coupon-top">
<div class="coupon-code">PROMO #{pr.codigo}</div>
<div class="coupon-discount">{pr.descuento}%</div>
<div class="coupon-name">{pr.nombre}</div>
</div>
<div class="coupon-bottom">
<div>
<div class="coupon-conditions-title">Válido al comprar:</div>
<ul class="coupon-conditions-list">
{condiciones_html}
</ul>
</div>
<div class="coupon-barcode"></div>
</div>
</div>"""

    # Usamos textwrap.dedent para asegurarnos de que no queden espacios a la izquierda
    html_final = textwrap.dedent(f"""
    <div class="coupon-sheet">
        {html_cupones}
    </div>
    """)

    st.markdown(html_final, unsafe_allow_html=True)


# --- Pantalla: mantenimiento ---
def pantalla_mantenimiento():
    boton_volver()
    
    st.markdown('<div class="action-container">', unsafe_allow_html=True)
    st.header("✏️ Mantenimiento")
    
    st.markdown("""
    <div class="info-box">
        <h4>📋 Requisitos del archivo</h4>
        <p>El archivo debe ser de texto (<code>.dsl</code> o <code>.txt</code>) y contener los siguientes comandos:</p>
        <ul>
            <li><code>AGREGAR PRODUCTO [código] ... FIN</code></li>
            <li><code>ACTUALIZAR PRODUCTO [código] ... FIN</code></li>
            <li><code>ELIMINAR PRODUCTO [código]</code></li>
            <li><code>AGREGAR PROMOCION [código] ... FIN</code></li>
            <li><code>ACTUALIZAR PROMOCION [código] ... FIN</code></li>
            <li><code>ELIMINAR PROMOCION [código]</code></li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    with st.container():
        archivo = st.file_uploader("Subir archivo", type=["dsl", "txt"], label_visibility="collapsed", key="mant")
        
        if archivo is not None:
            # Este CSS dinámico oculta el "+" y el texto solo cuando hay un archivo
            st.markdown("<style>[data-testid='stFileUploaderDropzoneInstructions'] { display: none !important; }</style>", unsafe_allow_html=True)
            st.write("")
            
            # Centramos el botón usando 3 columnas
            c1, c2, c3 = st.columns([1, 2, 1])
            with c2:
                if st.button("🚀 Ejecutar mantenimiento", type="primary", use_container_width=True):
                    try:
                        comandos = parse_mantenimiento(archivo.read().decode("utf-8"))
                        errores = ejecutar_mantenimiento(comandos, service)
                        if errores:
                            st.warning(f"{len(errores)} error(es) semántico(s):")
                            for e in errores:
                                st.error(e.mensaje)
                        else:
                            st.success(f"✅ {len(comandos)} comando(s) ejecutado(s) sin errores.")
                    except ErrorSintactico as e:
                        st.error(f"❌ Error sintáctico: {e.mensaje}")
                    except Exception as e:
                        st.exception(e)
                
    st.markdown('</div>', unsafe_allow_html=True)

# --- Pantalla: compras ---
def pantalla_compras():
    boton_volver()
    
    st.markdown('<div class="action-container">', unsafe_allow_html=True)
    st.header("🛒 Realizar Compras")
    
    st.markdown("""
    <div class="info-box">
        <h4>📋 Requisitos del archivo</h4>
        <p>El archivo debe ser de texto (<code>.dsl</code> o <code>.txt</code>) y contener los siguientes comandos:</p>
        <ul>
            <li>Debe empezar con la palabra <code>COMPRA</code> y terminar con <code>FIN</code>.</li>
            <li>Dentro, una lista de productos: <code>PRODUCTO [código]</code>.</li>
            <li>Opcionalmente, la cantidad: <code>CANTIDAD [número]</code>.</li>
        </ul>
        <p><i>Ejemplo: <code>COMPRA PRODUCTO 2 CANTIDAD 5 PRODUCTO 5 FIN</code></i></p>
    </div>
    """, unsafe_allow_html=True)

    with st.container():
        archivo = st.file_uploader("Subir archivo", type=["dsl", "txt"], label_visibility="collapsed", key="compra")
        
        if archivo is not None:
            st.markdown("<style>[data-testid='stFileUploaderDropzoneInstructions'] { display: none !important; }</style>", unsafe_allow_html=True)
            st.write("")
            
            c1, c2, c3 = st.columns([1, 2, 1])
            with c2:
                if st.button("🛒 Realizar compras", type="primary", use_container_width=True):
                    try:
                        comandos = parse_compras(archivo.read().decode("utf-8"))
                        compras, errores = ejecutar_compras(comandos, service)
                        
                        for i, c in enumerate(compras, 1):
                            st.success(f"✅ Compra #{i} — TOTAL: ${c.importe_total}")
                            st.dataframe(
                                [{"Producto": l.nombre, "Cantidad": l.cantidad,
                                  "Precio unit.": float(l.precio_unitario),
                                  "% desc.": float(l.porcentaje_descuento),
                                  "Importe": float(l.importe)}
                                 for l in c.lineas],
                                use_container_width=True, hide_index=True,
                            )
                            if c.promociones_aplicadas:
                                st.caption(f"Promociones aplicadas: {c.promociones_aplicadas}")
                            st.divider()
                        for e in errores:
                            st.error(e.mensaje)
                    except ErrorSintactico as e:
                        st.error(f"❌ Error sintáctico: {e.mensaje}")
                    except Exception as e:
                        st.exception(e)
                
    st.markdown('</div>', unsafe_allow_html=True)

# --- Pantalla: historial ---
def pantalla_historial():
    boton_volver()
    st.header("📜 Historial de Compras")
    
    compras = service.listar_compras()
    if not compras:
        st.info("No hay compras registradas todavía. Ir a la sección de Compras para hacer una")
        return

    st.markdown(f"**{len(compras)} ticket(s) registrado(s)**")

    html_tickets = ""
    # Recorremos las compras (invertidas para ver la más nueva primero)
    for i, c in enumerate(reversed(compras), 1):
        nro_ticket = len(compras) - i + 1
        
        # Armar las filas de la tabla SIN indentación
        filas_html = ""
        for l in c.lineas:
            desc = f"Desc: {l.porcentaje_descuento}%" if l.porcentaje_descuento > 0 else ""
            detalle = f"${float(l.precio_unitario):.2f} x {l.cantidad} {('| ' + desc) if desc else ''}"
            
            filas_html += f"""<tr>
<td>
<span class="item-name">{l.nombre}</span>
<span class="item-detail">#{l.codigo_producto} — {detalle}</span>
</td>
<td class="right" style="vertical-align: middle;">${float(l.importe):.2f}</td>
</tr>"""
            
        # Promos aplicadas
        promos_html = ""
        if c.promociones_aplicadas:
            promos_str = ", ".join([str(p) for p in c.promociones_aplicadas])
            promos_html = f"<div style='font-size: 11px; text-align: center; color: #666; margin-top: 10px;'>Promos aplicadas: {promos_str}</div>"

        # Todo el ticket sin indentación
        html_tickets += f"""<div class="receipt-wrapper">
<div class="receipt">
<div class="receipt-header">
<h2>SUPERMERCADO DSL</h2>
<p>Ticket #{nro_ticket:04d}</p>
<p>Fecha: 27/10/2026 - 8:15</p>
</div>
<div class="receipt-divider"></div>
<table class="receipt-table">
<thead>
<tr>
<th>Producto</th>
<th class="right">Total</th>
</tr>
</thead>
<tbody>
{filas_html}
</tbody>
</table>
<div class="receipt-divider"></div>
{promos_html}
<div class="receipt-total-box">
<div class="total-label">Total Pago</div>
<div class="total-amount">${float(c.importe_total):.2f}</div>
</div>
<div class="receipt-footer">
<div class="receipt-barcode"></div>
¡Gracias por tu compra! :)
</div>
</div>
</div>"""

    # Envolver todo en la grilla y limpiar cualquier espacio residual
    html_final = textwrap.dedent(f"""
    <div class="receipt-grid">
    {html_tickets}
    </div>
    """)

    st.markdown(html_final, unsafe_allow_html=True)

# # --- Pantalla: resumen ---
# def pantalla_resumen():
#     boton_volver()
#     st.header("📊 Resumen del Supermercado")

#     prods = service.listar_productos()
#     promos = service.listar_promociones()
#     compras = service.listar_compras()

#     total_ventas = sum((c.importe_total for c in compras), Decimal("0"))

#     c1, c2, c3, c4 = st.columns(4)
#     c1.metric("Productos", len(prods))
#     c2.metric("Promociones", len(promos))
#     c3.metric("Compras", len(compras))
#     c4.metric("Recaudación", f"${total_ventas:.2f}")

#     if compras:
#         st.subheader("Últimas compras")
#         for i, c in enumerate(reversed(compras[-5:]), 1):
#             st.write(f"Compra #{len(compras)-i+1} — Total ${c.importe_total}")


# --- Dispatch ---
p = pantalla_actual()
{
    "menu": pantalla_menu,
    "productos": pantalla_productos,
    "promociones": pantalla_promociones,
    "mantenimiento": pantalla_mantenimiento,
    "compras": pantalla_compras,
    "historial": pantalla_historial,
}.get(p, pantalla_menu)()