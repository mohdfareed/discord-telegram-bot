__all__ = ["setup_logging"]

import logging
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path

from rich.logging import RichHandler
from rich.text import Text

WARN_MODULES = ["asyncio", "discord", "telegram", "httpcore", "httpx"]
"""Modules for which to log warnings and above."""


def setup_logging(debug: bool, log_file: Path) -> None:
    """Setup logging for the application."""
    root_logger = logging.getLogger()

    root_logger.setLevel(logging.DEBUG if debug else logging.INFO)
    root_logger.addHandler(console_handler(debug))
    root_logger.addHandler(file_handler(log_file))

    for module in WARN_MODULES:  # Reduce log level for non-debug modules
        logging.getLogger(module).setLevel(logging.WARNING)


def console_handler(debug: bool) -> logging.Handler:
    handler = RichHandler(markup=True, show_path=False)
    handler.setFormatter(
        logging.Formatter(r"%(message)s [bright_black]\[%(name)s][/]")
    )
    handler.setLevel(logging.DEBUG if debug else logging.INFO)
    return handler


def file_handler(log_file: Path) -> logging.Handler:
    class StripMarkupFilter(logging.Filter):
        def filter(self, record: logging.LogRecord) -> bool:
            if hasattr(record, "msg") and isinstance(record.msg, str):
                record.msg = Text.from_markup(
                    Text.from_ansi(record.msg).plain
                ).plain
            return True  # filter rich markup and ansi escape codes

    log_file.parent.mkdir(parents=True, exist_ok=True)
    log_file.touch(exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    file_header = f"[{timestamp}]" + "=" * (80 - 2 - len(timestamp) - 1)
    with open(log_file, "a") as file:
        file.write(file_header + "\n")

    file = RotatingFileHandler(
        log_file, maxBytes=2**10, backupCount=0, delay=True
    )

    file.addFilter(StripMarkupFilter())
    file.setLevel(logging.NOTSET)
    file.setFormatter(
        logging.Formatter(
            r"[%(asctime)s.%(msecs)03d] %(levelname)-8s "
            r"%(message)s [%(name)s:%(filename)s:%(lineno)d]",
            datefmt=r"%Y-%m-%d %H:%M:%S",
        )
    )
    return file
