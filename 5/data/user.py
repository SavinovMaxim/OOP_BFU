from dataclasses import dataclass, field
from typing import Optional


@dataclass(order=True)
class User:
    id: int
    name: str
    login: str
    password: str = field(repr=False)
    email: Optional[str] = None
    address: Optional[str] = None
