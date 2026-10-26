# Entregable 3 - Juan Martín Berglavaz y Camila García

Quisimos hacer una GUI para la demo. El programa funciona con o sin interfaz (con menú desde la terminal).

COmo había que instalar varias librerías, decidimos dockerizar para quue nos sea más fácil y xa evitar problemas de compatibilidad. Acá están las dos maneras de correrlo:

## Ejecución con Python (sin Docker)

    python3 -m venv .venv
    source .venv/bin/activate      # Windows: .venv\Scripts\activate
    pip install -r requirements.txt
    python3 main.py                 # menú de consola

Para GUI (opcional):
    streamlit run app.py

## Ejecución con Docker (opcional)

    docker compose build
    docker compose run --rm menu    # menú de consola
    docker compose up gui           # GUI en http://localhost:8501
    docker compose run --rm tests   # correr tests

El informe está en la carpeta principal.