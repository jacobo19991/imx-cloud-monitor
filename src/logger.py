import os
import logging
from logging.handlers import RotatingFileHandler

# Asegurar que exista el directorio logs
LOGS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)

def setup_logger(name: str, log_file: str, level=logging.INFO) -> logging.Logger:
    """Configura y devuelve un logger con rotación de archivos."""
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Manejador de archivo con rotación (max 5MB por archivo, guarda 3 backups)
    file_path = os.path.join(LOGS_DIR, log_file)
    file_handler = RotatingFileHandler(
        file_path, maxBytes=5*1024*1024, backupCount=3, encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    
    # Manejador de consola
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Evitar duplicados si se llama varias veces
    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
    return logger

# Loggers preconfigurados
bot_logger = setup_logger('Bot', 'bot.log')
error_logger = setup_logger('Error', 'errors.log', level=logging.ERROR)
alerts_logger = setup_logger('Alerts', 'alerts.log')
