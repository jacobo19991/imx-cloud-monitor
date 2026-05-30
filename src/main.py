import time
from src.config import BUY_PRICE, SELL_PRICE, CHECK_INTERVAL, STOP_LOSS_PRICE, DEBUG_TELEGRAM
from src.market import MarketFetcher
from src.paper_trading import PaperTradingEngine
from src.database import init_db
from src.logger import bot_logger, error_logger
from src.telegram_service import test_telegram_connection, send_safe_telegram_message

def main():
    bot_logger.info("Iniciando IMX Cloud Monitor con SQLite...")
    
    # 1. Inicializar Base de Datos
    init_db()
    
    # 2. Prueba de conexión a Telegram (sólo si DEBUG_TELEGRAM está habilitado)
    if DEBUG_TELEGRAM:
        test_telegram_connection()
    else:
        bot_logger.info("Telegram Debug mode: OFF")
    
    # 3. Inicializar Componentes
    market = MarketFetcher()
    engine = PaperTradingEngine()
    
    # Alerta de inicio
    start_msg = (
        f"🚀 <b>¡Bot Sniper Iniciado!</b>\n\n"
        f"👁️ Vigilando: <b>IMX/USDT</b>\n"
        f"📉 Compra &lt;= <b>${BUY_PRICE}</b>\n"
        f"📈 Venta &gt;= <b>${SELL_PRICE}</b>\n"
        f"🛑 Stop Loss &lt;= <b>${STOP_LOSS_PRICE}</b>\n\n"
        f"💾 Modo: <i>Paper Trading (SQLite)</i>"
    )
    send_safe_telegram_message(start_msg)
    
    # 4. Bucle Principal
    while True:
        try:
            current_price = market.get_current_price('IMX/USDT')
            
            if current_price:
                # Procesar precio y lógica de paper trading
                action_taken = engine.process_tick(current_price, BUY_PRICE, SELL_PRICE, STOP_LOSS_PRICE)
                
                if action_taken:
                    bot_logger.info("Operación completada en el ciclo actual.")
            
            # Esperar hasta la próxima verificación
            time.sleep(CHECK_INTERVAL)
            
        except KeyboardInterrupt:
            bot_logger.info("Bot detenido manualmente por el usuario (Ctrl+C).")
            break
        except Exception as e:
            error_logger.error(f"Error crítico en el bucle principal: {e}")
            time.sleep(10) # Pequeña pausa antes de reintentar

if __name__ == "__main__":
    main()
