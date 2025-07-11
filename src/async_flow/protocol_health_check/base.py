from typing import Protocol

from src.async_flow.models.config import Server


class HealthCheckStrategy(Protocol):
    async def check_health(self, server: Server) -> bool:
        """
        Perform a health check on the given server.

        :param server: The server to check.
        :return: True if the server is healthy, False otherwise.
        """
        pass