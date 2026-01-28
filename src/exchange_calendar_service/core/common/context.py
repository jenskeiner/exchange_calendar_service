from .cache import ExchangeCalendarCache
from dataclasses import dataclass


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


@dataclass
class Context(metaclass=Singleton):
    """A singleton class that represents a global application context."""

    # The cache for exchange calendars.
    cache: ExchangeCalendarCache = None
