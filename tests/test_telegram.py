import pytest
import os
import sys

# Asegurar que la ruta src sea accesible durante el test
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.config import TELEGRAM_ENABLED
from src.telegram_service import send_safe_telegram_message

def test_telegram_degraded_mode(monkeypatch):
    """Prueba que el bot no se caiga al intentar enviar un mensaje sin credenciales."""
    # Desactivamos telegram
    monkeypatch.setattr("src.telegram_service.TELEGRAM_ENABLED", False)
    
    # Intentamos enviar un mensaje
    result = send_safe_telegram_message("Test message")
    
    # En modo degradado debería retornar True (interceptado) sin lanzar excepción
    assert result is True
