"""Shop model for provisioning shop details into a system."""

import re
from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class Shop:
    """Represents a shop instance with details used for system provisioning."""

    shop_id: str
    name: str
    owner: str
    address: str
    phone: str
    email: str
    category: str
    description: Optional[str] = None
    website: Optional[str] = None
    is_active: bool = True
    tags: list[str] = field(default_factory=list)

    _EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    _PHONE_RE = re.compile(r"^\+?[\d\s\-().]{7,20}$")

    def __post_init__(self) -> None:
        if not self._EMAIL_RE.match(self.email):
            raise ValueError(f"Invalid email address: {self.email!r}")
        if not self._PHONE_RE.match(self.phone):
            raise ValueError(f"Invalid phone number: {self.phone!r}")

    def provision(self) -> dict:
        """Return a dictionary of shop details suitable for system provisioning."""
        return asdict(self)

    def __repr__(self) -> str:
        return f"Shop(shop_id={self.shop_id!r}, name={self.name!r}, owner={self.owner!r})"
