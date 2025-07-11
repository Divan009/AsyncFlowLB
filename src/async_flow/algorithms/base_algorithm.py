from abc import ABC, abstractmethod
from typing import List

from src.async_flow.models.config import Server


class BaseAlgorithm(ABC):
    @abstractmethod
    async def select_server(self, server_list: List[Server]) -> Server:

        """
        :param server_list: List of available servers.
        Select a server based on the algorithm.
        Must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement this method.")


