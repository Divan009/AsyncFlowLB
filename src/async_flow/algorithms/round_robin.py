from src.async_flow.algorithms.base_algorithm import BaseAlgorithm


# this leads to concurrency issues
# multiple concurrent calls can lead to race conditions,
# resulting in inconsistent current_index values.

# f the server_list changes (servers added or removed),
# the current_index might become out of sync, potentially
# causing unexpected behavior or errors.
# class RoundRobinAlg(BaseAlgorithm):
#     def __init__(self):
#         self.current_index = -1  # Keeps track of the last selected server
#
#     def select_server(self, server_list):
#         """
#         Implements Round Robin algorithm to select the next server.
#         """
#         if not server_list:
#             raise ValueError("No servers available to select.")
#
#         self.current_index = (self.current_index + 1) % len(server_list)
#         return server_list[self.current_index]


import asyncio
from typing import List, Dict, Any
from src.async_flow.algorithms.base_algorithm import BaseAlgorithm


class RoundRobinAlg(BaseAlgorithm):
    def __init__(self):
        self.current_index = -1  # Keeps track of the last selected server
        self.lock = asyncio.Lock()  # Ensures thread-safe access

    async def select_server(self, server_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Implements Round Robin algorithm to select the next server in a thread-safe manner.
        """
        if not server_list:
            raise ValueError("No servers available to select.")

        async with self.lock:
            self.current_index = (self.current_index + 1) % len(server_list)
            selected_server = server_list[self.current_index]

        return selected_server
