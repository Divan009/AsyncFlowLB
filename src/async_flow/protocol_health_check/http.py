import aiohttp
import asyncio

from src.async_flow.logger import get_logger
from src.async_flow.models.config import Server
from src.async_flow.protocol_health_check.base import HealthCheckStrategy


class HttpHealthCheckStrategy(HealthCheckStrategy):
    def __init__(self, session: aiohttp.ClientSession, timeout: int, health_check_path: str):
        self.session = session
        self.timeout = timeout
        self.health_check_path = health_check_path
        self.logger = get_logger(self.__class__.__name__)

    async def check_health(self, server: Server) -> bool:
        url = f'http://{server.host}:{server.port}{self.health_check_path}'
        try:
            async with self.session.get(url, timeout=self.timeout) as response:
                if response.status == 200:
                    self.logger.debug(f"HTTP health check passed for {server}.")
                    return True
                else:
                    self.logger.warning(f"HTTP health check failed for {server}: Status {response.status}.")
                    return False
        except asyncio.TimeoutError:
            self.logger.warning(f"HTTP health check timed out for {server}.")
            return False
        except aiohttp.ClientError as e:
            self.logger.warning(f"HTTP health check client error for {server}: {e}.")
            return False
