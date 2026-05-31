import os
from sqlalchemy import Column, Integer, String, Float, DateTime, func, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

class BotState(Base):
    __tablename__ = 'bot_state'
    id = Column(Integer, primary_key=True)
    usdt_balance = Column(Float, nullable=False)
    imx_balance = Column(Float, nullable=False)
    last_buy_price = Column(Float, default=0.0)
    last_sell_price = Column(Float, default=0.0)
    status = Column(String, default='ACTIVE')
    position_open = Column(Integer, default=0)
    entry_price = Column(Float, default=0.0)
    entry_timestamp = Column(DateTime)
    total_profit = Column(Float, default=0.0)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class Trade(Base):
    __tablename__ = 'trades'
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=func.now())
    symbol = Column(String, nullable=False)
    action = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    quantity = Column(Float, nullable=False)
    usdt_balance = Column(Float, nullable=False)
    imx_balance = Column(Float, nullable=False)
    pnl = Column(Float, default=0.0)
    notes = Column(String)

# Database URL para la API asíncrona
DB_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///data/trades.db")
if DB_URL.startswith("sqlite") and not DB_URL.startswith("sqlite+aiosqlite"):
    DB_URL = DB_URL.replace("sqlite://", "sqlite+aiosqlite://")

# Si usamos SQLite, necesitamos el check_same_thread=False
engine_kwargs = {}
if DB_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

sync_db_url = DB_URL.replace("+asyncpg", "+psycopg2").replace("+aiosqlite", "")
engine = create_engine(sync_db_url, **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
async_engine = create_async_engine(DB_URL, **engine_kwargs)
AsyncSessionLocal = sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)
