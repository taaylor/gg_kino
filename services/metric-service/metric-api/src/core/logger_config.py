import logging.config
from typing import Any

import dotenv
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE = dotenv.find_dotenv()


class LoggerSettings(BaseSettings):
    log_level: str = "DEBUG"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_default_handlers: list[str] = ["console"]

    logging: dict[str, Any] = {}

    model_config = SettingsConfigDict(
        env_prefix="LOG_",
        env_file=ENV_FILE,
        extra="ignore",
    )

    @model_validator(mode="after")
    def init_logging(self) -> "LoggerSettings":
        handlers_config = {
            "console": {
                "level": self.log_level,
                "class": "logging.StreamHandler",
                "formatter": "verbose",
            },
            "default": {
                "formatter": "default",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
            },
            "access": {
                "formatter": "access",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
            },
        }

        self.logging = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "verbose": {"format": self.log_format},
                "default": {"format": "%(levelname)s: %(message)s"},
                "access": {"format": "%(levelname)s: %(message)s"},
            },
            "handlers": handlers_config,
            "loggers": {
                "": {
                    "handlers": self.log_default_handlers,
                    "level": self.log_level,
                },
                "flask": {
                    "level": self.log_level,
                },
                "flask.app": {
                    "handlers": ["access"],
                    "level": self.log_level,
                    "propagate": False,
                },
            },
        }
        return self

    def apply(self) -> None:
        """Применить настройки логирования один раз при старте приложения."""
        logging.config.dictConfig(self.logging)
