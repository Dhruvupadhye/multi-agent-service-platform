import logging
import sys

def setup_logger(name: str = "office_automation") -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO) #the logger will output INFO, WARNING, ERROR, and CRITICAL messages, but will ignore DEBUG messages to keep your console clean. we can use DEBUG instead of INFO to see debug logs as well.

    if not logger.handlers:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger

logger = setup_logger()