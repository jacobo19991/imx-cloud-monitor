import os
from dotenv import load_dotenv

# Cargar variables del .env
load_dotenv()

# Validar que existan las credenciales
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Modo degradado: Si no hay token, se apaga Telegram pero el bot no se muere
TELEGRAM_ENABLED = bool(TELEGRAM_TOKEN and TELEGRAM_CHAT_ID)

# Configuraciones de trading
BUY_PRICE = float(os.getenv("BUY_PRICE", "0.1720"))
SELL_PRICE = float(os.getenv("SELL_PRICE", "0.1910"))
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "45"))

# Configuración Paper Trading
INITIAL_CAPITAL = float(os.getenv("INITIAL_CAPITAL", "100.0"))
TRADE_AMOUNT_USDT = float(os.getenv("TRADE_AMOUNT_USDT", "10.0"))
STOP_LOSS_PRICE = float(os.getenv("STOP_LOSS_PRICE", "0.150"))
MAX_OPEN_POSITION = float(os.getenv("MAX_OPEN_POSITION", "100.0"))
DEBUG_TELEGRAM = os.getenv("DEBUG_TELEGRAM", "false").lower() == "true"

