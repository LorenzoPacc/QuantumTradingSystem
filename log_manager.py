"""Log Manager - Rotazione log professionale"""
import logging
import logging.handlers
import json
from typing import Dict, Any

class DynamicLogManager:
    def __init__(self, config: Dict[str, Any], log_file: str = "bot.log"):
        self.enabled = config.get("enabled", True)
        
        if self.enabled:
            max_bytes = config.get("max_size_mb", 50) * 1024 * 1024
            backup_count = config.get("backup_count", 5)
            
            handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=max_bytes,
                backupCount=backup_count
            )
            
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            handler.setFormatter(formatter)
            
            root_logger = logging.getLogger()
            root_logger.addHandler(handler)
            root_logger.setLevel(logging.INFO)
            
            logging.info("✅ Log rotation configurato")


def init_log_manager(log_file: str = "bot.log", config_path: str = "bot_improvements_config.json"):
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        return DynamicLogManager(config["log_rotation"], log_file)
    except Exception as e:
        print(f"❌ Errore init log manager: {e}")
        return DynamicLogManager({"enabled": False}, log_file)
