import asyncio
import os
from typing import List, Optional
from pydantic import Field, BaseModel, field_validator, ValidationError, PrivateAttr

from async_flow.enums import ProtocolType, AlgorithmType


class Listen(BaseModel):
    host: str = Field(default_factory=lambda: os.getenv('LB_LISTEN_HOST', '0.0.0.0'))
    port: int = Field(..., ge=1, le=65535)
    protocol: str

    @field_validator('protocol')
    def validate_protocol(cls, v):
        v = v.lower()
        if v not in [protocol.value for protocol in ProtocolType]:
            raise ValidationError(f"Invalid protocol: {v}")
        return v

    @field_validator('host')
    def validate_host(cls, v):
        import socket
        try:
            socket.gethostbyname(v)
            return v
        except socket.error:
            raise ValueError(f"Invalid Server's IP address: {v}")


class Server(BaseModel):
    host: str
    port: int = Field(..., ge=1, le=65535)
    weight: int = Field(..., ge=1)
    active_connections: int = 0
    healthy: bool = True

    # Private attribute for lock
    _lock: asyncio.Lock = PrivateAttr(default_factory=asyncio.Lock)

    @field_validator('host')
    def validate_host(cls, v):
        import socket
        try:
            socket.inet_aton(v)
            return v
        except socket.error:
            raise ValueError(f"Invalid Server's IP address: {v}")


class LoadBalance(BaseModel):
    algorithms: str
    servers: List[Server]

    @field_validator('algorithms')
    def validate_algorithms(cls, v):
        v = v.lower()
        valid_algorithms = [algorithm.value for algorithm in AlgorithmType]
        if v not in valid_algorithms:
            raise ValueError(f"Invalid load balancing algorithm '{v}'. Valid options are: {', '.join(valid_algorithms)}")
        return v


class HealthCheck(BaseModel):
    interval: int = Field(gt=0, description="Interval must be a positive integer")
    timeout: int = Field(gt=0, description="Timeout must be a positive integer")
    path: str = Field(default="/health", description="Path must start with '/'")
    retries: Optional[int] = Field(default=3, gt=0, description="Retries must be a positive integer")

    @field_validator('path')
    def validate_path(cls, v):
        if not v.startswith('/'):
            raise ValueError("Health check path must start with '/'")
        return v


class LoadBalancerConfig(BaseModel):
    listen: Listen
    load_balance: LoadBalance
    health_check: HealthCheck

