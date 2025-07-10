from src.async_flow.algorithms.base_algorithm import BaseAlgorithm
from src.async_flow.algorithms.least_connections import LeastConnectionsAlg
from src.async_flow.algorithms.round_robin import RoundRobinAlg
from src.async_flow.algorithms.weighted_round_robin import WeightedRoundRobinAlg
from src.async_flow.enums import AlgorithmType


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
        print(algorithm_type)
        match algorithm_type:
            case AlgorithmType.ROUND_ROBIN.value:
                return RoundRobinAlg()
            case AlgorithmType.WEIGHTED_ROUND_ROBIN.value:
                return WeightedRoundRobinAlg()
            case AlgorithmType.LEAST_CONNECTIONS.value:
                return LeastConnectionsAlg()
            case _:
                raise ValueError()
