import os
import aiosqlite
import secrets
from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="IMX Cloud Monitor Dashboard")
security = HTTPBasic()

# Credenciales desde .env (o por defecto para desarrollo)
DASHBOARD_USER = os.getenv("DASHBOARD_USER", "admin")
DASHBOARD_PASS = os.getenv("DASHBOARD_PASS", "admin123")

def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, DASHBOARD_USER)
    correct_password = secrets.compare_digest(credentials.password, DASHBOARD_PASS)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

# Rutas absolutas para evitar problemas al ejecutar desde distintos directorios
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "trades.db")
TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")

# Configurar Jinja2 para las plantillas HTML
templates = Jinja2Templates(directory=TEMPLATES_DIR)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, username: str = Depends(verify_credentials)):
    return templates.TemplateResponse(request=request, name="index.html")

@app.get("/api/status")
async def get_status(username: str = Depends(verify_credentials)):
    """Devuelve el estado general del bot (Capital, IMX, PnL, Posición)."""
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            
            # Obtener el último estado del bot
            async with db.execute("SELECT * FROM bot_state ORDER BY timestamp DESC LIMIT 1") as cursor:
                state = await cursor.fetchone()
            
            # Obtener métricas de trades
            async with db.execute("SELECT COUNT(*) as total_trades FROM trades") as cursor:
                row = await cursor.fetchone()
                total_trades = row["total_trades"]
                
        if state:
            return {
                "status": "online",
                "usdt_balance": state["usdt_balance"],
                "imx_balance": state["imx_balance"],
                "total_profit": state.get("total_profit", 0.0),
                "has_open_position": state["imx_balance"] > 0,
                "total_trades": total_trades,
                "last_update": state["timestamp"]
            }
        return {"status": "offline", "message": "No hay datos en bot_state"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/trades")
async def get_trades(username: str = Depends(verify_credentials)):
    """Devuelve el historial de operaciones para la tabla y el gráfico."""
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            
            # Obtener los últimos 50 trades
            async with db.execute("SELECT * FROM trades ORDER BY timestamp DESC LIMIT 50") as cursor:
                rows = await cursor.fetchall()
                trades = [dict(row) for row in rows]
                
        return {"trades": trades}
    except Exception as e:
        return {"status": "error", "message": str(e)}
