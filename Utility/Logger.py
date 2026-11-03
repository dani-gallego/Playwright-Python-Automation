import logging
from datetime import datetime

from Config.ProjectPaths import PROJECT_PATHS


class Logger:
    """
    Centralized logging utility.
    """

    LOG_FOLDER = PROJECT_PATHS.logs

    _logger = None

    # =========================================================
    # INITIALIZE LOGGER
    # =========================================================

    @classmethod
    def initialize(cls):

        if cls._logger is not None:
            return cls._logger

        cls.LOG_FOLDER.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        log_file = (
            cls.LOG_FOLDER
            / f"Automation_{timestamp}.log"
        )

        logger = logging.getLogger(
            "PlaywrightAutomation"
        )

        logger.setLevel(logging.DEBUG)

        formatter = logging.Formatter(
            "%(asctime)s | "
            "%(levelname)s | "
            "%(message)s"
        )

        file_handler = logging.FileHandler(
            log_file,
            encoding="utf-8"
        )

        file_handler.setLevel(
            logging.DEBUG
        )

        file_handler.setFormatter(
            formatter
        )

        console_handler = logging.StreamHandler()

        console_handler.setLevel(
            logging.INFO
        )

        console_handler.setFormatter(
            formatter
        )

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        cls._logger = logger

        return logger

    # =========================================================
    # INFO
    # =========================================================

    @classmethod
    def info(cls, message: str):

        logger = cls.initialize()

        logger.info(message)

    # =========================================================
    # DEBUG
    # =========================================================

    @classmethod
    def debug(cls, message: str):

        logger = cls.initialize()

        logger.debug(message)

    # =========================================================
    # WARNING
    # =========================================================

    @classmethod
    def warning(cls, message: str):

        logger = cls.initialize()

        logger.warning(message)

    # =========================================================
    # ERROR
    # =========================================================

    @classmethod
    def error(cls, message: str):

        logger = cls.initialize()

        logger.error(message)

    # =========================================================
    # EXCEPTION
    # =========================================================

    @classmethod
    def exception(cls, message: str):

        logger = cls.initialize()

        logger.exception(message)
