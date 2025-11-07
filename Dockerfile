# Usar imagen base de Python
FROM python:3.11-slim

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema (si es necesario)
RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements.txt e instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY . .

# Exponer el puerto que usa Gradio
EXPOSE 7860

# Variables de entorno por defecto
ENV GRADIO_HOST=0.0.0.0
ENV GRADIO_PORT=7860

# Comando para ejecutar la aplicación
CMD ["python", "main.py"]

