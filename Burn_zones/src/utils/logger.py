import functools
import time
import logging
import os

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "logs")
LOG_DIR = os.path.abspath(LOG_DIR)
os.makedirs(LOG_DIR, exist_ok=True)
LOG_PATH = os.path.join(LOG_DIR, "app.log")

logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def get_logger():
    return logging.getLogger("burn_zones")

def log_process(func):
    """Decorador para registrar inicio, fin, duración y errores"""
    logger = get_logger()
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        logger.info(f"🔄 START {func.__name__}")
        start = time.time()
        try:
            result = func(self, *args, **kwargs)
            elapsed = round(time.time() - start, 3)
            logger.info(f"✅ DONE {func.__name__} in {elapsed}s")
            return result
        except Exception as e:
            elapsed = round(time.time() - start, 3)
            logger.exception(f"❌ ERROR {func.__name__} after {elapsed}s: {e}")
            raise
    return wrapper
