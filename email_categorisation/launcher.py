import logging
import sys
import sentry_sdk
from gunicorn.app.base import BaseApplication
from gunicorn.glogging import Logger
from loguru import logger
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration
from main import app
import config

log_level_mapping = {
    'development': logging.DEBUG,
    'test': logging.DEBUG,
    'production': logging.INFO,
    'staging': logging.INFO,
}

LOG_LEVEL = log_level_mapping.get(config.config.ENVIRONMENT, logging.ERROR)


class InterceptHandler(logging.Handler):
    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


class StubbedGunicornLogger(Logger):
    def setup(self, cfg):
        handler = logging.NullHandler()
        self.error_logger = logging.getLogger("gunicorn.error")
        self.error_logger.addHandler(handler)
        self.access_logger = logging.getLogger("gunicorn.access")
        self.access_logger.addHandler(handler)
        self.error_logger.setLevel(LOG_LEVEL)
        self.access_logger.setLevel(LOG_LEVEL)


class StandaloneApplication(BaseApplication):
    """Gunicorn application for the new project."""

    def __init__(self, application, options=None):
        self.options = options or {}
        self.application = application
        super().__init__()

    def load_config(self):
        _config = {key: value for key, value in self.options.items() if key in self.cfg.settings and value is not None}
        for key, value in _config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application


def setup_logging():
    intercept_handler = InterceptHandler()
    logging.basicConfig(handlers=[intercept_handler], level=LOG_LEVEL)
    logging.root.handlers = [intercept_handler]
    logging.root.setLevel(LOG_LEVEL)

    seen = set()
    for name in [
        *logging.root.manager.loggerDict.keys(),
        "gunicorn",
        "gunicorn.access",
        "gunicorn.error",
        "uvicorn",
        "uvicorn.access",
        "uvicorn.error",
    ]:
        if name not in seen:
            seen.add(name.split(".")[0])
            logging.getLogger(name).handlers = [intercept_handler]

    logger.configure(handlers=[{"sink": sys.stdout, "serialize": config.config.JSON_LOGS, "level": LOG_LEVEL}])
    logger.add("logs/email_categorisation.log", rotation="500 MB")


if __name__ == "__main__":
    # Initialize Sentry
    sentry_sdk.init(
        release=app.version,
        environment=str(config.config.ENVIRONMENT),
        dsn=config.config.SENTRY_DSN,
        integrations=[
            StarletteIntegration(),
            FastApiIntegration(),
        ],
        traces_sample_rate=1,
    )

    setup_logging()

    server_options = {
        "bind": f"{config.config.APP_HOST}:{config.config.APP_PORT}",
        "workers": config.config.GUNICORN_WORKERS,
        "accesslog": "-",
        "errorlog": "-",
        "worker_class": "uvicorn.workers.UvicornWorker",
        "logger_class": StubbedGunicornLogger,
    }

    StandaloneApplication(app, server_options).run()
