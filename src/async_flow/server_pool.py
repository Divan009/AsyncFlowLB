import asyncio


class ServerPool:
    def __init__(self, servers):
        self.servers = servers # List of Pydantic Server instances from models/config
        self.lock = asyncio.Lock()

    def get_all_servers(self):
        return self.servers

    def get_servers(self):
        return [s for s in self.servers if s.healthy]

    async def mark_unhealthy(self, server) -> bool:
        async with server._lock:
            if server.healthy:
                server.healthy = False
                return True
        return False

    async def mark_healthy(self, server) -> bool:
        async with server._lock:
            if not server.healthy:
                server.healthy = True
                return True
        return False
