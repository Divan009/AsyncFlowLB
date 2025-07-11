import asyncio
from typing import List

from src.async_flow.algorithms.base_algorithm import BaseAlgorithm
from src.async_flow.models.config import Server


class RoundRobinAlg(BaseAlgorithm):
    def __init__(self):
        self.current_index = -1  # Keeps track of the last selected server
        self.lock = asyncio.Lock()  # Ensures thread-safe access

    async def select_server(self, server_list: List[Server]) -> Server:
        """
        Implements Round Robin algorithm to select the next server in a thread-safe manner.
        """
        if not server_list:
            raise ValueError("No servers available to select.")

        async with self.lock:
            self.current_index = (self.current_index + 1) % len(server_list)
            selected_server = server_list[self.current_index]

        return selected_server
