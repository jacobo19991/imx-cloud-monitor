import os
import os
import secrets
from sqlalchemy import select, func
from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from typing import List, Optional, Any
from fastapi.responses import HTMLResponse, PlainTextResponse
import time
from dotenv import load_dotenv

START_TIME = time.time()

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

from src.models import AsyncSessionLocal, BotState, Trade
from sqlalchemy.exc import SQLAlchemyError

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

# --- MODELOS PYDANTIC (Fase 1: Tipado Fuerte) ---
class StatusResponse(BaseModel):
    status: str
    message: Optional[str] = None
    usdt_balance: Optional[float] = None
    imx_balance: Optional[float] = None
    total_profit: Optional[float] = None
    has_open_position: Optional[bool] = None
    total_trades: Optional[int] = None
    last_update: Optional[str] = None
    initial_capital: Optional[float] = None
    roi_percentage: Optional[float] = None
    win_rate: Optional[float] = None

class Trade(BaseModel):
    id: int
    timestamp: str
    type: str
    price: float
    amount_imx: float
    total_usdt: float

class TradesResponse(BaseModel):
    status: str = "success"
    message: Optional[str] = None
    trades: List[dict] = []  # Usamos dict temporalmente para mayor flexibilidad con SQLite

class HealthResponse(BaseModel):
    status: str
    version: str
    description: str
    checks: dict

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, username: str = Depends(verify_credentials)):
    return templates.TemplateResponse(request=request, name="index.html")

@app.get("/health", response_model=HealthResponse)
async def health_check(db: AsyncSession = Depends(get_db)):
    """Endpoint SRE (Fase 3: Observabilidad)."""
    db_ok = False
    try:
        await db.execute(select(1))
        db_ok = True
    except Exception:
        pass

    # Validación de entorno (Telegram Token existe)
    telegram_ok = bool(os.getenv("TELEGRAM_TOKEN"))

    is_healthy = db_ok and telegram_ok
    status_code = status.HTTP_200_OK if is_healthy else status.HTTP_503_SERVICE_UNAVAILABLE

    response = HealthResponse(
        status="pass" if is_healthy else "fail",
        version="2.0.0",
        description="IMX Cloud Monitor Health Status",
        checks={
            "database": "up" if db_ok else "down",
            "api:telegram_token": "configured" if telegram_ok else "missing"
        }
    )
    if not is_healthy:
        raise HTTPException(status_code=status_code, detail=response.dict())
    return response

@app.get("/metrics", response_class=PlainTextResponse)
async def get_metrics(db: AsyncSession = Depends(get_db)):
    """Endpoint SRE (Fase 3: Observabilidad) - Formato Prometheus."""
    uptime_seconds = time.time() - START_TIME
    
    total_trades = 0
    total_profit = 0.0
    
    try:
        result_trades = await db.execute(select(func.count(Trade.id)))
        total_trades = result_trades.scalar() or 0
        
        result_profit = await db.execute(select(BotState.total_profit).filter(BotState.id == 1))
        profit_scalar = result_profit.scalar()
        if profit_scalar is not None:
            total_profit = profit_scalar
    except Exception:
        pass

    metrics = [
        "# HELP imx_bot_uptime_seconds Tiempo de actividad del dashboard",
        "# TYPE imx_bot_uptime_seconds gauge",
        f"imx_bot_uptime_seconds {uptime_seconds:.2f}",
        "# HELP imx_bot_trades_total Total de operaciones ejecutadas",
        "# TYPE imx_bot_trades_total counter",
        f"imx_bot_trades_total {total_trades}",
        "# HELP imx_bot_pnl_usdt Profit and Loss acumulado en USDT",
        "# TYPE imx_bot_pnl_usdt gauge",
        f"imx_bot_pnl_usdt {total_profit}"
    ]
    
    return "\n".join(metrics) + "\n"

@app.get("/api/status", response_model=StatusResponse)
async def get_status(username: str = Depends(verify_credentials), db: AsyncSession = Depends(get_db)):
    """Devuelve el estado general del bot (Capital, IMX, PnL, Posición)."""
    try:
        # Obtener el último estado del bot
        result = await db.execute(select(BotState).filter(BotState.id == 1))
        state = result.scalars().first()
        
        # Obtener métricas de trades
        result_trades = await db.execute(select(func.count(Trade.id)))
        total_trades = result_trades.scalar() or 0
                
        if state:
            initial_capital = float(os.getenv("INITIAL_CAPITAL", "100.0"))
            profit = state.total_profit or 0.0
            roi = (profit / initial_capital) * 100 if initial_capital > 0 else 0.0
            
            # Estimación simple de Win Rate
            win_rate = 100.0 if profit > 0 else 0.0 
            
            return {
                "status": "online",
                "usdt_balance": state.usdt_balance,
                "imx_balance": state.imx_balance,
                "total_profit": profit,
                "has_open_position": state.imx_balance > 0,
                "total_trades": total_trades,
                "last_update": str(state.updated_at) if state.updated_at else None,
                "initial_capital": initial_capital,
                "roi_percentage": round(roi, 2),
                "win_rate": round(win_rate, 2)
            }
        return {"status": "offline", "message": "No hay datos en bot_state"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/trades", response_model=TradesResponse)
async def get_trades(username: str = Depends(verify_credentials), db: AsyncSession = Depends(get_db)):
    """Devuelve el historial de operaciones para la tabla y el gráfico."""
    try:
        result = await db.execute(select(Trade).order_by(Trade.timestamp.desc()).limit(50))
        trades = result.scalars().all()
        
        trades_dict = [{
            "id": t.id,
            "timestamp": str(t.timestamp),
            "symbol": t.symbol,
            "action": t.action,
            "price": t.price,
            "amount_imx": t.quantity,
            "total_usdt": t.quantity * t.price
        } for t in trades]
                
        return {"trades": trades_dict}
    except Exception as e:
        return {"status": "error", "message": str(e)}
