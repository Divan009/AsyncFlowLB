from async_flow.algorithms.least_connections import LeastConnectionsAlg
from async_flow.algorithms.round_robin import RoundRobinAlg
from async_flow.algorithms.weighted_round_robin import WeightedRoundRobinAlg
from async_flow.enums import AlgorithmType


class BaseAlgorithm:
    def select_server(self, server_list):

        """
        :param server_list: List of available servers.
        Select a server based on the algorithm.
        Must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement this method.")


class AlgorithmContext:
    def __init__(self, algorithm):
        self._algorithm = algorithm

    @property
    def algorithm(self):
        return self._algorithm

    @algorithm.setter
    def algorithm(self, algorithm):
        self._algorithm = algorithm

    def execute(self, server_list):
        return self._algorithm.select_server(server_list)


class AlgorithmFactory:
    def build(self, algorithm_type: str) -> BaseAlgorithm:
        match algorithm_type:
            case AlgorithmType.ROUND_ROBIN:
                return RoundRobinAlg()
            case AlgorithmType.WEIGHTED_ROUND_ROBIN:
                return WeightedRoundRobinAlg()
            case AlgorithmType.LEAST_CONNECTIONS:
                return LeastConnectionsAlg()
            case _:
                raise ValueError()

