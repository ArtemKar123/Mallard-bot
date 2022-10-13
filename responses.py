from dataclasses import dataclass
from enum import Enum


class ResponseType(Enum):
    TEXT = 1
    STICKER = 2
    VOICE = 3


@dataclass
class Response:
    """
    Represents response which is one of ResponseType
    """
    text: str
    type: ResponseType
