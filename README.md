# IMX Cloud Monitor 🚀☁️

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![SQLite](https://img.shields.io/badge/Database-SQLite-informational)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)

Un bot de monitorización automatizada y sistema de **Paper Trading** para el par IMX/USDT. Diseñado con una arquitectura modular orientada a despliegues en la nube (Cloud/DevOps).

## ☁️ Enfoque Cloud & DevOps

Este proyecto fue desarrollado aplicando buenas prácticas de infraestructura y desarrollo:
* **Persistencia Segura:** Uso de SQLite para almacenamiento ligero y rápido sin depender de servicios externos complejos.
* **Separación de Entornos:** Gestión estricta de credenciales a través de variables de entorno (`.env`).
* **Container-Ready:** Incluye configuración de Docker para un despliegue aislado y predecible en cualquier proveedor de nube (AWS, GCP, VPS local).
* **Notificaciones en Tiempo Real:** Integración con la API de Telegram con sanitización automática de mensajes para evitar fallos de formato.
* **Observabilidad:** Sistema de logging estructurado para facilitar la depuración en servidores remotos.

## 🛠️ Arquitectura del Sistema

- `src/main.py`: Orquestador principal.
- `src/paper_trading.py`: Motor lógico de simulación (Single Position Enforcement).
- `src/database.py`: Gestión de migraciones y consultas SQLite.
- `src/telegram_service.py`: Comunicación asíncrona y blindada con el usuario.

## 🚀 Instalación y Despliegue Local

### Requisitos Previos
- Python 3.11+
- Git

### Paso 1: Clonar e instalar
```bash
git clone https://github.com/tu-usuario/imx-cloud-monitor.git
cd imx-cloud-monitor
pip install -r requirements.txt
```

### Paso 2: Configuración
Crea tu archivo de entorno basándote en la plantilla de seguridad:
```bash
cp .env.example .env
```
Edita `.env` con tu token de Telegram y configuración de trading.

### Paso 3: Ejecución
```bash
python -m src.main
```

## 🐳 Despliegue con Docker (Recomendado para VPS)

Este proyecto está preparado para ejecutarse 24/7 en contenedores.

```bash
# Construir la imagen
docker build -t imx-cloud-monitor .

# Ejecutar el contenedor en segundo plano (montando el volumen de datos para persistir SQLite)
docker run -d --name imx_bot \
  -v $(pwd)/data:/app/data \
  --env-file .env \
  imx-cloud-monitor
```

## 📋 Próximos Pasos (Roadmap)
- [ ] Integración con el dashboard web analítico (FastAPI).
- [ ] Despliegue CI/CD usando GitHub Actions.
- [ ] Conexión a exchange real mediante APIs seguras.
