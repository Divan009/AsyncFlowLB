import asyncio
import logging
from typing import Optional, Protocol

import aiohttp

from src.async_flow.enums import ProtocolType
from src.async_flow.models.config import HealthCheck as HealthCheckConfig
from src.async_flow.protocol_health_check.base import ProtocolStrategy
from src.async_flow.protocol_health_check.http import HttpHealthCheckStrategy
from src.async_flow.protocol_health_check.tcp import TcpHealthCheckStrategy

from src.async_flow.server_pool import ServerPool


class HealthCheckProtocolStrategyFactory:
    def build(
            protocol_type: str,
            session: Optional[aiohttp.ClientSession] = None,
            timeout: int = 5,
            health_check_path: str = "/health"
    ) -> ProtocolStrategy:
        match protocol_type:
            case ProtocolType.TCP.value:
                return TcpHealthCheckStrategy(timeout)
            case ProtocolType.HTTP.value:
                return HttpHealthCheckStrategy(session, timeout, health_check_path)
            case _:
                raise ValueError(f"Unknown protocol type: {protocol_type}")


class HealthCheck:
    def __init__(self, server_pool: ServerPool, config: HealthCheckConfig, protocol: str = 'http'):
        self.server_pool = server_pool
        self.config = config
        self.protocol = protocol
        self.interval = config.interval
        self.health_check_path = config.path
        self.timeout = config.timeout

        self.running = False
        self.session: Optional[aiohttp.ClientSession] = None
        self.logger = logging.getLogger(self.__class__.__name__)

        # Retry settings
        self.max_retries = getattr(config, 'retries', 3)
        self.retry_delay = getattr(config, 'retry_delay', 2)  # seconds

        self.health_check_strategy: Optional[ProtocolStrategy] = None

    async def start(self):
        """Initialize resources and start the health checker."""
        if self.protocol == 'http':
            self.session = aiohttp.ClientSession()
            self.health_check_strategy = HealthCheckProtocolStrategyFactory.build(
                protocol_type=self.protocol,
                session=self.session,
                timeout=self.config.timeout,
                health_check_path=self.health_check_path
            )
        elif self.protocol == 'tcp':
            self.health_check_strategy = HealthCheckProtocolStrategyFactory.build(
                protocol_type=self.protocol,
                timeout=self.config.timeout
            )
        else:
            self.logger.error(f"Unsupported protocol: {self.protocol}")
            raise ValueError(f"Unsupported protocol: {self.protocol}")

        self.running = True
        self.logger.info("Health Checker has begun.")
        await asyncio.create_task(self.run())

    async def run(self):
        """Continuously perform health checks at specified intervals."""
        try:
            while self.running:
                servers = self.server_pool.get_all_servers()
                if not servers:
                    self.logger.warning("No servers available for health checks.")
                else:
                    tasks = [self.check_server(server) for server in servers ]
                    await asyncio.gather(*tasks, return_exceptions=True)
                await asyncio.sleep(self.interval)
        except asyncio.CancelledError:
            self.logger.info("HealthChecker task cancelled.")
        finally:
            await self.close()


    async def check_server(self, server):
        """Check the health of a single server based on the protocol."""
        for attempt in range(1, self.max_retries + 1):
            try:
                is_healthy = await self.health_check_strategy.check_health(server)
                if is_healthy:
                    await self.mark_healthy(server)
                else:
                    raise ValueError("Health check failed.")
                break
            except Exception as e:
                self.logger.error(
                    f"Error checking server {server}: {e} (Attempt {attempt}/{self.max_retries})"
                )

                if attempt < self.max_retries:
                    backoff = self.retry_delay * 2 ** (attempt - 1)
                    self.logger.info(f"Retrying in {backoff} seconds...")
                    await asyncio.sleep(backoff)
                else:
                    await self.mark_unhealthy(server)

    async def mark_healthy(self, server):
        """Mark a server as healthy."""
        old_mark = await self.server_pool.mark_healthy(server)
        if old_mark:
            self.logger.info(f"Server {server} marked as healthy.")

    async def mark_unhealthy(self, server):
        """Mark a server as unhealthy."""
        old_mark = await self.server_pool.mark_unhealthy(server)
        if old_mark:
            self.logger.info(f"Server {server} marked as unhealthy.")

    async def close(self):
        """Clean up resources."""
        if self.running:
            self.running = False
            self.logger.info("Shutting down HealthChecker.")
        if self.session and not self.session.closed:
            await self.session.close()
            self.logger.info("HTTP session closed.")