"""
Централизованная конфигурация логирования для backend.
Использует loguru для единообразного логирования во всём приложении.
"""
import sys
from pathlib import Path

from loguru import logger

# Формат логов: время | уровень | модуль | сообщение
LOG_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
    "<level>{message}</level>"
)


def setup_logging(
    level: str = "INFO",
    log_to_file: bool = False,
    log_dir: str | Path | None = None,
) -> None:
    """
    Настраивает централизованное логирование.

    Args:
        level: Уровень логирования (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_to_file: Писать ли логи в файл
        log_dir: Директория для лог-файлов (по умолчанию backend/logs)
    """
    logger.remove()  # Сбрасываем стандартный handler loguru
    logger.add(
        sys.stderr,
        format=LOG_FORMAT,
        level=level,
        colorize=True,
    )

    if log_to_file and log_dir:
        log_path = Path(log_dir)
        log_path.mkdir(parents=True, exist_ok=True)
        logger.add(
            log_path / "app_{time:YYYY-MM-DD}.log",
            format=LOG_FORMAT,
            level=level,
            rotation="1 day",
            retention="7 days",
        )


# Импортировать в модулях: from core.logging_config import logger
