
from datetime import datetime
from ipaddress import IPv4Address, IPv6Address
from typing import Literal

from pydantic import BaseModel, Field


class SecurityLog(BaseModel):
    timestamp: datetime

    ip_address: IPv4Address | IPv6Address

    username: str = Field(
        min_length=1,
        max_length=100
    )

    event_type: Literal[
        "login_failed",
        "login_success",
        "unauthorized_access"
    ]

    status: Literal[
        "failed",
        "success"
    ]
