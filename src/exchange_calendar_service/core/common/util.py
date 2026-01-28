from enum import Enum
from logging import Logger
from collections.abc import Iterable
from typing import Literal, TypeVar


def log_iterable(log: Logger, lines: Iterable[str], level: str):
    for line in lines:
        log.log(level, line)


def log_multi_line(message: str, level: str):
    log_iterable(message.splitlines(), level)


T = TypeVar("T", bound=Enum)


def get_enum_key_literal_type(enum: type[T]) -> type:
    return Literal[*[item.name for item in enum]]
