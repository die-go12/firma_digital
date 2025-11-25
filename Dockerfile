# Usamos una imagen base ligera de Python 3.10
FROM python:3.10-slim

# Evitamos que Python genere archivos temporales .pyc
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Instalamos dependencias del sistema necesarias para criptografía (gcc, libssl)
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiamos los requisitos e instalamos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos TODO el código del proyecto al contenedor
COPY . .

# Creamos las carpetas de almacenamiento dentro del contenedor

RUN mkdir -p storage/keys storage/certs storage/signed_pdfs storage/temp

# Exponemos el puerto 8000 (donde corre FastAPI)
EXPOSE 8000

# Comando para iniciar la aplicación
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
