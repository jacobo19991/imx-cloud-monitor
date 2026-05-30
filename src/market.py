import ccxt
from src.logger import error_logger, bot_logger

class MarketFetcher:
    def __init__(self):
        self.exchange = ccxt.mexc({
            'enableRateLimit': True,
        })
        
    def get_current_price(self, symbol: str = 'IMX/USDT') -> float:
        """Obtiene el último precio de un activo. Retorna None en caso de error."""
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            return float(ticker['last'])
        except ccxt.NetworkError as e:
            error_logger.error(f"Error de red al consultar MEXC: {e}")
            return None
        except ccxt.ExchangeError as e:
            error_logger.error(f"Error del exchange MEXC: {e}")
            return None
        except Exception as e:
            error_logger.error(f"Error inesperado al obtener precio: {e}")
            return None
