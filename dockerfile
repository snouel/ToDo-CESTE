# Usa una imagen base de Python ligera (Slim) para reducir el tamaño
FROM python:3.11-slim-buster

# Establecer variables de entorno
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Crear y establecer el directorio de trabajo
WORKDIR /app

# Copiar el archivo de dependencias y optimizar la instalación
COPY requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Copiar el resto del código fuente de la aplicación
COPY . /app

# Exponer el puerto por defecto de Uvicorn
EXPOSE 8000

# Comando para iniciar la aplicación con Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]