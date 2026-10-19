from dataclasses import dataclass
from typing import Optional

@dataclass
class ErrorSemantico(Exception):
    mensaje: str
    contexto: Optional[str] = None

@dataclass
class ErrorSintactico(Exception):
    mensaje: str
    linea: Optional[int] = None
    columna: Optional[int] = None