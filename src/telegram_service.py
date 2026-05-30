import requests
import re
from src.config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, TELEGRAM_ENABLED
from src.logger import error_logger, alerts_logger

def escape_telegram_html(text: str) -> str:
    """
    Escapa los caracteres especiales para evitar errores 'can't parse entities' en Telegram,
    pero mantiene intactas las etiquetas HTML permitidas (b, i, u, s, code, pre).
    """
    allowed_tags = ['b', '/b', 'i', '/i', 'u', '/u', 's', '/s', 'code', '/code', 'pre', '/pre']
    
    # Reemplazamos los ampersands sueltos primero
    text = re.sub(r'&(?!(amp|lt|gt|quot|apos);)', '&amp;', text)
    
    def tag_replacer(match):
        content = match.group(1)
        tag_name = content.strip().lower()
        if tag_name in allowed_tags:
            return f"<{content}>"
        else:
            return f"&lt;{content}&gt;"
            
    safe_text = text.replace('<=', '&lt;=').replace('>=', '&gt;=')
    safe_text = re.sub(r'<(.*?)>', tag_replacer, safe_text)
    
    return safe_text

def send_safe_telegram_message(message: str, use_html: bool = True) -> bool:
    """
    Intenta enviar con parse_mode="HTML". Si falla por formato, reenvía como texto plano.
    """
    if not TELEGRAM_ENABLED:
        alerts_logger.info(f"[TELEGRAM DESACTIVADO] Mensaje interceptado:\n{message}")
        print(f"\n[MODO DEGRADADO] Mensaje que iría a Telegram:\n{message}\n")
        return True
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    
    # Preparar el payload
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": escape_telegram_html(message) if use_html else message
    }
    
    if use_html:
        payload["parse_mode"] = "HTML"
        
    # Diagnóstico
    token_preview = f"{TELEGRAM_TOKEN[:8]}..." if TELEGRAM_TOKEN and len(TELEGRAM_TOKEN) > 8 else "INVALID"
    print(f"\n--- DIAGNÓSTICO TELEGRAM ---")
    print(f"DEBUG CHAT_ID: {TELEGRAM_CHAT_ID}")
    print(f"DEBUG TOKEN: {token_preview}")
    print(f"INTENTANDO HTML: {use_html}")
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        status_code = response.status_code
        
        print(f"STATUS: {status_code}")
        print(f"RESPUESTA: {response.text}")
        print(f"----------------------------\n")
        
        # Validar si Telegram devolvió OK
        data = response.json()
        
        if not data.get("ok"):
            # Ocurrió un error
            error_msg = f"Telegram devolvió error ({status_code}): {response.text}"
            print(f"❌ ERROR: {error_msg}")
            error_logger.error(error_msg)
            print(f"TEXTO ORIGINAL ENVIADO:\n{message}")
            
            # Si fue un error HTTP 400 y estábamos usando HTML, intentar texto plano
            if status_code == 400 and use_html:
                print("⚠️ Falló el modo HTML. Reintentando como TEXTO PLANO...")
                error_logger.warning("Fallo envío HTML. Usando fallback de texto plano.")
                
                # Limpiar las etiquetas principales para el modo texto
                plain_message = message.replace('<b>', '').replace('</b>', '')
                plain_message = plain_message.replace('<i>', '').replace('</i>', '')
                
                return send_safe_telegram_message(plain_message, use_html=False)
            
            return False
            
        # Si todo fue exitoso
        alerts_logger.info("Mensaje de Telegram enviado correctamente.")
        return True
        
    except requests.exceptions.RequestException as e:
        error_logger.error(f"Error de red enviando mensaje a Telegram: {e}")
        print(f"❌ ERROR DE RED: {e}")
        return False

def send_telegram_message(message: str) -> bool:
    """Alias para mantener compatibilidad con otras funciones."""
    return send_safe_telegram_message(message, use_html=True)

def test_telegram_connection():
    """Prueba la conexión a Telegram antes de iniciar el bot."""
    if not TELEGRAM_ENABLED:
        print("⚠️ Telegram desactivado. Ignorando prueba de conexión.")
        return
        
    print("Iniciando prueba de conexión con Telegram...")
    send_safe_telegram_message("✅ <b>Prueba</b> de conexión Telegram")
