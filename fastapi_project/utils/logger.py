import logging
import os

def get_logger():
    logger = logging.getLogger("auth_logger")
    logger.setLevel(logging.INFO)
    log_path = "D:/project/ELK-Track/fastapi_project/log/auth.log"
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    
    if not logger.handlers:
        handler = logging.FileHandler(log_path, mode="a", encoding="utf-8")
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(handler)
    return logger
