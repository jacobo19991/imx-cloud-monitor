# Utilizar una imagen base oficial y ligera de Python
FROM python:3.11-slim

# Establecer variables de entorno para evitar que Python genere archivos .pyc 
# y para que el log se muestre en tiempo real (unbuffered)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Crear un directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar el archivo de dependencias primero para aprovechar el caché de Docker
COPY requirements.txt .

# Instalar dependencias del sistema y de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el código fuente al contenedor
COPY . .

# Crear el volumen de datos para la base de datos SQLite y logs
VOLUME ["/app/data", "/app/logs"]

# Exponer puerto para el Dashboard Web (Usado por web-dashboard)
EXPOSE 8000

# Comando por defecto (Sobrescribible por docker-compose)
CMD ["python", "-m", "src.main"]
