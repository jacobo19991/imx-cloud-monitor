import os
from src.logger import error_logger
from src.models import Base, engine, SessionLocal, BotState, Trade
from sqlalchemy.exc import SQLAlchemyError

def init_db():
    """Crea las tablas en la base de datos usando SQLAlchemy."""
    try:
        # Create data directory if using sqlite
        db_url = os.getenv("DATABASE_URL", "sqlite:///data/trades.db")
        if db_url.startswith("sqlite"):
            db_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
            if not os.path.exists(db_dir):
                os.makedirs(db_dir)

        # Crear tablas (idealmente manejado por Alembic en producción, pero útil para local/testing)
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        error_logger.error(f"Error inicializando base de datos SQLAlchemy: {e}")

def save_trade(symbol: str, action: str, price: float, quantity: float, usdt_balance: float, imx_balance: float, pnl: float = 0.0, notes: str = ""):
    """Guarda un registro de la operación en el historial usando SQLAlchemy."""
    db = SessionLocal()
    try:
        new_trade = Trade(
            symbol=symbol,
            action=action,
            price=price,
            quantity=quantity,
            usdt_balance=usdt_balance,
            imx_balance=imx_balance,
            pnl=pnl,
            notes=notes
        )
        db.add(new_trade)
        db.commit()
    except SQLAlchemyError as e:
        error_logger.error(f"Error guardando trade (ORM): {e}")
        db.rollback()
    finally:
        db.close()

def get_trades(limit: int = 50):
    """Obtiene el historial de las últimas transacciones."""
    db = SessionLocal()
    try:
        trades = db.query(Trade).order_by(Trade.timestamp.desc()).limit(limit).all()
        # Convertir a dict para retrocompatibilidad
        return [{
            "id": t.id,
            "timestamp": str(t.timestamp),
            "symbol": t.symbol,
            "action": t.action,
            "price": t.price,
            "quantity": t.quantity,
            "usdt_balance": t.usdt_balance,
            "imx_balance": t.imx_balance,
            "pnl": t.pnl,
            "notes": t.notes
        } for t in trades]
    except SQLAlchemyError as e:
        error_logger.error(f"Error obteniendo trades (ORM): {e}")
        return []
    finally:
        db.close()

def get_bot_state() -> dict:
    """Recupera el estado actual del bot."""
    db = SessionLocal()
    try:
        state = db.query(BotState).filter(BotState.id == 1).first()
        if state:
            return {
                "id": state.id,
                "usdt_balance": state.usdt_balance,
                "imx_balance": state.imx_balance,
                "last_buy_price": state.last_buy_price,
                "last_sell_price": state.last_sell_price,
                "status": state.status,
                "position_open": state.position_open,
                "entry_price": state.entry_price,
                "entry_timestamp": str(state.entry_timestamp) if state.entry_timestamp else None,
                "total_profit": state.total_profit,
                "updated_at": str(state.updated_at) if state.updated_at else None
            }
        return None
    except SQLAlchemyError as e:
        error_logger.error(f"Error obteniendo estado del bot (ORM): {e}")
        return None
    finally:
        db.close()

def update_bot_state(usdt_balance: float, imx_balance: float, last_buy_price: float = 0.0, last_sell_price: float = 0.0, status: str = 'ACTIVE', position_open: int = 0, entry_price: float = 0.0, entry_timestamp: str = None):
    """Actualiza o inserta el estado del bot."""
    db = SessionLocal()
    try:
        state = db.query(BotState).filter(BotState.id == 1).first()
        if state:
            state.usdt_balance = usdt_balance
            state.imx_balance = imx_balance
            state.last_buy_price = last_buy_price
            state.last_sell_price = last_sell_price
            state.status = status
            state.position_open = position_open
            state.entry_price = entry_price
            if entry_timestamp:
                state.entry_timestamp = entry_timestamp
            
            # Calcular profit estimado simple si hay posición cerrada
            if position_open == 0 and imx_balance == 0:
                # Este es un cálculo básico. Idealmente se pasa el PnL exacto
                from src.config import INITIAL_CAPITAL
                state.total_profit = usdt_balance - INITIAL_CAPITAL
        else:
            new_state = BotState(
                id=1,
                usdt_balance=usdt_balance,
                imx_balance=imx_balance,
                last_buy_price=last_buy_price,
                last_sell_price=last_sell_price,
                status=status,
                position_open=position_open,
                entry_price=entry_price,
                entry_timestamp=entry_timestamp,
                total_profit=0.0
            )
            db.add(new_state)
        
        db.commit()
    except SQLAlchemyError as e:
        error_logger.error(f"Error actualizando estado del bot (ORM): {e}")
        db.rollback()
    finally:
        db.close()
