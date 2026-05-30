import sqlite3
import os
from src.logger import error_logger

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
DB_PATH = os.path.join(DB_DIR, 'trades.db')

def get_connection():
    """Retorna una conexión a la base de datos SQLite."""
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR)
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Crea las tablas si no existen y aplica migraciones de columnas."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Tabla de operaciones (trades)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            symbol TEXT NOT NULL,
            action TEXT NOT NULL,
            price REAL NOT NULL,
            quantity REAL NOT NULL,
            usdt_balance REAL NOT NULL,
            imx_balance REAL NOT NULL,
            pnl REAL,
            notes TEXT
        )
        ''')
        
        # Tabla de estado del bot
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS bot_state (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            usdt_balance REAL NOT NULL,
            imx_balance REAL NOT NULL,
            last_buy_price REAL,
            last_sell_price REAL,
            status TEXT DEFAULT 'ACTIVE',
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Migraciones dinámicas: intentar agregar nuevas columnas si no existen
        try:
            cursor.execute("ALTER TABLE bot_state ADD COLUMN position_open INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
            pass # Ya existe
            
        try:
            cursor.execute("ALTER TABLE bot_state ADD COLUMN entry_price REAL DEFAULT 0.0")
        except sqlite3.OperationalError:
            pass # Ya existe
            
        try:
            cursor.execute("ALTER TABLE bot_state ADD COLUMN entry_timestamp DATETIME")
        except sqlite3.OperationalError:
            pass # Ya existe
        
        conn.commit()
    except Exception as e:
        error_logger.error(f"Error inicializando base de datos: {e}")
    finally:
        if conn:
            conn.close()

def save_trade(symbol: str, action: str, price: float, quantity: float, usdt_balance: float, imx_balance: float, pnl: float = 0.0, notes: str = ""):
    """Guarda un registro de la operación en el historial."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO trades (symbol, action, price, quantity, usdt_balance, imx_balance, pnl, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (symbol, action, price, quantity, usdt_balance, imx_balance, pnl, notes))
        conn.commit()
    except Exception as e:
        error_logger.error(f"Error guardando trade: {e}")
    finally:
        if conn:
            conn.close()

def get_trades(limit: int = 50):
    """Obtiene el historial de las últimas transacciones."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM trades ORDER BY timestamp DESC LIMIT ?", (limit,))
        return [dict(row) for row in cursor.fetchall()]
    except Exception as e:
        error_logger.error(f"Error obteniendo trades: {e}")
        return []
    finally:
        if conn:
            conn.close()

def get_bot_state() -> dict:
    """Recupera el estado actual del bot."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM bot_state WHERE id = 1")
        row = cursor.fetchone()
        return dict(row) if row else None
    except Exception as e:
        error_logger.error(f"Error obteniendo estado del bot: {e}")
        return None
    finally:
        if conn:
            conn.close()

def update_bot_state(usdt_balance: float, imx_balance: float, last_buy_price: float = 0.0, last_sell_price: float = 0.0, status: str = 'ACTIVE', position_open: int = 0, entry_price: float = 0.0, entry_timestamp: str = None):
    """Actualiza o inserta el estado del bot."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM bot_state WHERE id = 1")
        if cursor.fetchone():
            cursor.execute('''
                UPDATE bot_state
                SET usdt_balance = ?, imx_balance = ?, last_buy_price = ?, last_sell_price = ?, status = ?, position_open = ?, entry_price = ?, entry_timestamp = COALESCE(?, entry_timestamp), updated_at = CURRENT_TIMESTAMP
                WHERE id = 1
            ''', (usdt_balance, imx_balance, last_buy_price, last_sell_price, status, position_open, entry_price, entry_timestamp))
        else:
            cursor.execute('''
                INSERT INTO bot_state (id, usdt_balance, imx_balance, last_buy_price, last_sell_price, status, position_open, entry_price, entry_timestamp)
                VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (usdt_balance, imx_balance, last_buy_price, last_sell_price, status, position_open, entry_price, entry_timestamp))
            
        conn.commit()
    except Exception as e:
        error_logger.error(f"Error actualizando estado del bot: {e}")
    finally:
        if conn:
            conn.close()
