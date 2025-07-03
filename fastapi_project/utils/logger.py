import logging
import os
from pythonjsonlogger import jsonlogger

def get_auth_logger():
    logger = logging.getLogger("auth_logger")
    logger.setLevel(logging.INFO)
    log_path = "D:/project/ELK-Track/fastapi_project/log/auth.log"
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    
    if not logger.handlers:
        handler = logging.FileHandler(log_path, mode="a", encoding="utf-8")
        formatter = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(message)s') # json 형식으로 로그 변환 
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger

def get_access_logger():
    logger = logging.getLogger("access_logger")
    logger.setLevel(logging.INFO)
    log_path = "D:/project/ELK-Track/fastapi_project/log/access.log"
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    
    if not logger.handlers:
        handler = logging.FileHandler(log_path, mode="a", encoding="utf-8")
        formatter = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger