import logging
import sys
from app.core.config import settings


def setup_logging():
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] [%(name)s:%(lineno)d] - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

    # Silence excessively verbose external loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    logger = logging.getLogger("climatetwin")
    logger.info(f"Initialized ClimateTwin AI Backend Logging (Level: {logging.getLevelName(log_level)})")
    return logger


logger = setup_logging()

