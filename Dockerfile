FROM python:3.14-slim

WORKDIR /app

# Copiar requirements primero (cache-friendly: si no cambia, no reinstala)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código
COPY . .

# Comando por defecto: menú de consola
CMD ["python3", "main.py"]