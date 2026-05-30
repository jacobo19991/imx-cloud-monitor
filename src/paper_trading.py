from datetime import datetime
from src.database import get_bot_state, update_bot_state, save_trade
from src.telegram_service import send_safe_telegram_message
from src.logger import bot_logger, alerts_logger
from src.config import INITIAL_CAPITAL, TRADE_AMOUNT_USDT, MAX_OPEN_POSITION

class PaperTradingEngine:
    def __init__(self):
        self._ensure_initial_state()
        
    def _ensure_initial_state(self):
        """Asegura que el bot tenga un estado inicial en la base de datos."""
        state = get_bot_state()
        if not state:
            bot_logger.info(f"Inicializando estado de Paper Trading con {INITIAL_CAPITAL} USDT")
            update_bot_state(
                usdt_balance=INITIAL_CAPITAL,
                imx_balance=0.0,
                last_buy_price=0.0,
                last_sell_price=0.0,
                status='ACTIVE',
                position_open=0,
                entry_price=0.0,
                entry_timestamp=None
            )

    def process_tick(self, current_price: float, buy_target: float, sell_target: float, stop_loss: float) -> bool:
        """Evalúa el precio actual contra las reglas y ejecuta operaciones simuladas si corresponde."""
        state = get_bot_state()
        if not state:
            return False
            
        usdt_balance = state['usdt_balance']
        imx_balance = state['imx_balance']
        last_buy_price = state['last_buy_price']
        
        action_taken = False
        
        # Lógica central: Verificar si YA EXISTE una posición abierta
        has_open_position = imx_balance > 0
        
        # 1. Lógica de Compra (Buy) - SOLO SI NO HAY POSICIÓN ABIERTA
        if current_price <= buy_target:
            if has_open_position:
                # Ya hay posición, la compra se bloquea.
                bot_logger.info("Compra bloqueada porque ya existe posición abierta")
                return False
            else:
                usdt_to_spend = min(TRADE_AMOUNT_USDT, usdt_balance)
                
                if usdt_to_spend > 0:
                    imx_bought = usdt_to_spend / current_price
                    new_usdt = usdt_balance - usdt_to_spend
                    new_imx = imx_bought
                    
                    timestamp_now = datetime.now().isoformat()
                    
                    update_bot_state(
                        usdt_balance=new_usdt,
                        imx_balance=new_imx,
                        last_buy_price=current_price,
                        last_sell_price=state['last_sell_price'],
                        status='OPEN',
                        position_open=1,
                        entry_price=current_price,
                        entry_timestamp=timestamp_now
                    )
                    
                    save_trade('IMX/USDT', 'BUY', current_price, imx_bought, new_usdt, new_imx, 0.0, "Compra por debajo de BUY_PRICE")
                    
                    self._send_buy_alert(current_price, imx_bought, new_usdt)
                    bot_logger.info(f"COMPRA SIMULADA: {imx_bought:.2f} IMX a ${current_price:.4f}")
                    action_taken = True
                    
        # 2. Lógica de Venta (Take Profit o Stop Loss) - SOLO SI HAY POSICIÓN ABIERTA
        elif has_open_position:
            bot_logger.info("Posición abierta, esperando venta")
            
            if current_price >= sell_target:
                # TAKE PROFIT
                usdt_earned = imx_balance * current_price
                cost_basis = imx_balance * last_buy_price if last_buy_price > 0 else 0
                pnl = usdt_earned - cost_basis
                
                new_usdt = usdt_balance + usdt_earned
                new_imx = 0.0
                
                update_bot_state(
                    usdt_balance=new_usdt,
                    imx_balance=new_imx,
                    last_buy_price=last_buy_price,
                    last_sell_price=current_price,
                    status='CLOSED',
                    position_open=0,
                    entry_price=0.0,
                    entry_timestamp=None
                )
                
                save_trade('IMX/USDT', 'SELL', current_price, imx_balance, new_usdt, new_imx, pnl, "Venta por Take Profit")
                
                self._send_sell_alert(current_price, pnl, new_usdt)
                bot_logger.info(f"VENTA SIMULADA (Take Profit): {imx_balance:.2f} IMX a ${current_price:.4f}. PnL: ${pnl:.2f}")
                action_taken = True

            elif current_price <= stop_loss:
                # STOP LOSS
                usdt_earned = imx_balance * current_price
                cost_basis = imx_balance * last_buy_price if last_buy_price > 0 else 0
                pnl = usdt_earned - cost_basis
                
                new_usdt = usdt_balance + usdt_earned
                new_imx = 0.0
                
                update_bot_state(
                    usdt_balance=new_usdt,
                    imx_balance=new_imx,
                    last_buy_price=last_buy_price,
                    last_sell_price=current_price,
                    status='CLOSED',
                    position_open=0,
                    entry_price=0.0,
                    entry_timestamp=None
                )
                
                save_trade('IMX/USDT', 'STOP_LOSS', current_price, imx_balance, new_usdt, new_imx, pnl, "Venta por Stop Loss")
                
                self._send_sell_alert(current_price, pnl, new_usdt)
                bot_logger.warning(f"STOP LOSS EJECUTADO: {imx_balance:.2f} IMX a ${current_price:.4f}. PnL: ${pnl:.2f}")
                action_taken = True

        return action_taken

    def _send_buy_alert(self, price: float, quantity: float, usdt_balance: float):
        msg = (
            f"🟢 <b>Posición Abierta</b>\n\n"
            f"<b>Precio entrada:</b> ${price:.4f}\n"
            f"<b>Cantidad:</b> {quantity:.2f} IMX\n"
            f"<b>Capital restante:</b> ${usdt_balance:.2f} USDT"
        )
        send_safe_telegram_message(msg)

    def _send_sell_alert(self, price: float, pnl: float, usdt_balance: float):
        # Determinar el icono basado en PnL
        icon = "🔴" if pnl <= 0 else "🟢"
        
        msg = (
            f"{icon} <b>Posición Cerrada</b>\n\n"
            f"<b>Precio salida:</b> ${price:.4f}\n"
            f"<b>PnL:</b> ${pnl:.2f}\n"
            f"<b>Capital actualizado:</b> ${usdt_balance:.2f} USDT"
        )
        send_safe_telegram_message(msg)
