import asyncio
import random
from typing import Dict, List

from src.async_flow.algorithms.base_algorithm import BaseAlgorithm
from src.async_flow.models.config import Server


class LeastConnectionsAlg(BaseAlgorithm):
    def __init__(self):
        self._open_conn: Dict[Server, int] = {}
        self._lock = asyncio.Lock()

    async def select_server(self, server_list: List[Server]) -> Server:
        """
        Implements Least Connection algorithm to select the next server.
        """
        if not server_list:
            raise ValueError("No servers available to select.")

        async with self._lock:
            # Ensure every live server has a counter
            for server in server_list:
                self._open_conn.setdefault(server, 0)

            # Remove stale entries (servers that disappeared from the pool)
            stale = set(self._open_conn) - set(server_list)
            for s in stale:
                self._open_conn.pop(s, None)

            # need it to be random
            random.shuffle(server_list)
            chosen = min(server_list, key=self._open_conn.get)

            # request goes to this
            self._open_conn[chosen] += 1
            return chosen

    async def release_server(self, server: Server) -> None:
        async with self._lock:
            if server not in self._open_conn:
                # log this bcz why do we have unknown server - warning?
                return

            if self._open_conn[server] == 0:
                # double-release
                # log at WARNING?
                return

            self._open_conn[server] -= 1
