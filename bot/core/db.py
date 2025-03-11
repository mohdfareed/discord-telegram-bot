__all__ = ["Database", "JSONDataBase"]

import logging
from pathlib import Path
from threading import Lock
from typing import Protocol

from pydantic import BaseModel


class Database(Protocol):
    """Database interface for storing models."""

    def save(self, model: BaseModel) -> None:
        """Save a model to the database."""
        ...

    def load[T: BaseModel](self, model: T) -> T:
        """Load a model from the database."""
        ...


class JSONDataBase(Database):
    """Database for storing models as JSON files."""

    lock = Lock()

    def __init__(self, path: Path) -> None:
        self.logger = logging.getLogger(type(self).__name__)
        self.path = path
        with JSONDataBase.lock:
            self.path.mkdir(parents=True, exist_ok=True)

    def save(self, model: BaseModel) -> None:
        with JSONDataBase.lock:
            self._path(model).touch(exist_ok=True)
            self._path(model).write_text(model.model_dump_json(indent=2))

    def load[T: BaseModel](self, model: T) -> T:
        with JSONDataBase.lock:
            self._path(model).touch(exist_ok=True)
            return model.model_validate_json(
                self._path(model).read_text() or "{}"
            )

    def _path(self, model: BaseModel) -> Path:
        return self.path / f"{type(model).__name__.lower()}.json"
