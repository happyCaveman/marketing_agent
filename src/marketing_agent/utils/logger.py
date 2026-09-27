import logging 

from marketing_agent.config.settings import settings

def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    
    if logger.handlers:
        return logger
    
    logger.setLevel(settings.log_level)
    
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )
    
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger