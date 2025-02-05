from enum import Enum


class ProtocolType(Enum):
    HTTP = "http"
    TCP = "tcp"


class AlgorithmType(Enum):
    ROUND_ROBIN = "round_robin"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    LEAST_CONNECTIONS = "least_connections"
