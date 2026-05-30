# IMX Cloud Monitor ☁️🚀 (SaaS Edition)

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=FastAPI&logoColor=white)
![Docker](https://img.shields.io/badge/Docker_Compose-Ready-2496ED.svg?logo=docker)
![Status](https://img.shields.io/badge/Status-Production_Ready-success.svg)

**IMX Cloud Monitor** es una arquitectura de microservicios diseñada para simular, operar y monitorear activos financieros (par IMX/USDT) con grado de producción. 

Construido bajo el paradigma **Cloud-Native**, este sistema aísla el motor de trading de la interfaz analítica web, garantizando alta disponibilidad, concurrencia asíncrona y seguridad integral.

---

## 🏛️ Arquitectura de Microservicios

El sistema está orquestado con **Docker Compose** y cuenta con Health Checks de autorreparación:

1. **Trading Engine (`trading-engine`)**
   - Motor lógico aislado en Python.
   - Implementa control estricto de Posición Única (Single Position Enforcement).
   - Comunicación en tiempo real vía Telegram API.
2. **Web Dashboard API (`web-dashboard`)**
   - Interfaz gráfica SPA construida con TailwindCSS y Chart.js.
   - Backend asíncrono con **FastAPI** y `aiosqlite`.
   - Protegido por autenticación `HTTPBasic`.
3. **Capa de Persistencia Compartida**
   - Base de datos SQLite y volúmenes de logs compartidos mediante montajes persistentes de Docker (`/app/data`).

---

## 🚀 Despliegue con un Solo Comando (Cloud-Ready)

Este proyecto está diseñado para desplegarse en cualquier VPS (AWS EC2, DigitalOcean, Azure) de manera determinista.

### Prerrequisitos
- Docker Engine & Docker Compose
- Clonar el repositorio y configurar credenciales:
  ```bash
  cp .env.example .env
  # Edita .env con tus credenciales seguras
  ```

### Arrancar la Infraestructura Completa
```bash
docker-compose up -d --build
```
> [!TIP]
> Esto levantará ambos servicios en paralelo. El dashboard web estará disponible inmediatamente de forma segura en `http://localhost:8000`.

### Monitoreo Operativo
Verifica el estado de salud de los contenedores (Health Checks):
```bash
docker ps
docker-compose logs -f trading-engine
```

---

## 🔒 Seguridad Implementada

- **Aislamiento de Red:** El motor de trading no expone ningún puerto al exterior.
- **Autenticación Web:** La interfaz financiera está blindada por variables de entorno administradas por FastAPI (Basic Auth).
- **Asincronía Real:** La API web (`aiosqlite`) nunca bloquea el Event Loop del bot, previniendo cuelgues (Database Locks).

---

## 🗺️ Roadmap de Monetización (Visión SaaS)

El proyecto está diseñado para evolucionar hacia una plataforma **SaaS (Software as a Service) Multi-Tenant**:

- **Fase 1 (MVP Actual):** Motor de Paper Trading automatizado con métricas privadas y notificaciones instantáneas.
- **Fase 2 (Suscripción):** Ofrecer señales de Telegram automáticas como servicio (Premium Alerts) para canales privados, cobrando membresía mensual.
- **Fase 3 (Integración CEX):** Conectar el motor directamente a las APIs de Binance o Bybit (CCXT) para ejecutar operaciones con dinero real.
- **Fase 4 (Multi-Tenant Dashboard):** Cada usuario registrado en el sistema tendrá su propia sub-cuenta administrada, cobrando comisiones por volumen operado bajo el modelo *Hedge Fund As-A-Service*.
