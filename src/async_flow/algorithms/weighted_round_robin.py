from src.async_flow.algorithms.base_algorithm import BaseAlgorithm


class WeightedRoundRobinAlg(BaseAlgorithm):
    def __init__(self):
        self.current_index = -1  # Keeps track of the last selected server

    def select_server(self, server_list):
        """
        Implements Round Robin algorithm to select the next server.
        """
        if not server_list:
            raise ValueError("No servers available to select.")

        self.current_index = (self.current_index + 1) % len(server_list)
        return server_list[self.current_index]
