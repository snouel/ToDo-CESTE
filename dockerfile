# Usa una imagen base de Python ligera (Slim) para reducir el tamaño
FROM python:3.11-slim-bookworm

# Establecer variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Crear y establecer el directorio de trabajo
WORKDIR /app

# Actualizamos paquetes del sistema (buena práctica de seguridad)
RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/*

# Actualiza pip y setuptools a la última versión segura
RUN pip install --upgrade pip setuptools wheel

# Copiar el archivo de dependencias y optimizar la instalación
COPY requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Copiar el resto del código fuente de la aplicación
COPY . /app

# Exponer el puerto por defecto de Uvicorn
EXPOSE 8000

# Comando para iniciar la aplicación con Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]