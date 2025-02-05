import asyncio

from async_flow.logger import get_logger

from async_flow.models.config import Server


class TcpHealthCheckStrategy:
    def __init__(self, timeout: int):
        self.timeout = timeout
        self.logger = get_logger(self.__class__.__name__)

    async def check_health(self, server: Server) -> bool:
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(server.address, server.port),
                timeout=self.timeout
            )
            writer.close()
            await writer.wait_closed()
            self.logger.debug(f"TCP health check passed for {server}.")
            return True
        except (asyncio.TimeoutError, ConnectionRefusedError) as e:
            self.logger.warning(f"TCP health check failed for {server}: {e}.")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error during TCP health check for {server}: {e}.")
            return False
