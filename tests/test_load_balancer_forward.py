# tests/test_load_balancer_forward.py

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from async_flow.core import LoadBalancer
from async_flow.models.config import LoadBalancerConfig
from aiohttp import web

@pytest.fixture
def mock_config():
    """Fixture to create a valid LoadBalancerConfig."""
    return LoadBalancerConfig(
        listen={
            "host": "127.0.0.1",
            "port": 8080,
            "protocol": "http"
        },
        health_check={
            "interval": 5,
            "timeout": 2,
            "path": "/health",
            "retries": 3,
            "retry_delay": 1
        },
        load_balance={
            "algorithms": "round_robin",
            "servers": [
                {"host": "127.0.0.1", "port": 9000, "weight": 1},
                {"host": "127.0.0.2", "port": 9001, "weight": 1}
            ]
        }
    )

@pytest.fixture
def mock_health_check():
    """Fixture to mock the HealthCheck object."""
    health_check = AsyncMock()
    health_check.start = AsyncMock()
    health_check.close = AsyncMock()
    return health_check

@pytest.fixture
def mock_server_pool():
    """Fixture to mock the ServerPool object."""
    server_pool = MagicMock()
    server_pool.get_all_servers.return_value = [
        {"host": "127.0.0.1", "port": 9000, "weight": 1, "healthy": True},
        {"host": "127.0.0.2", "port": 9001, "weight": 1, "healthy": True}
    ]
    server_pool.get_healthy_servers.return_value = [
        {"host": "127.0.0.1", "port": 9000, "weight": 1, "healthy": True},
        {"host": "127.0.0.2", "port": 9001, "weight": 1, "healthy": True}
    ]
    return server_pool

@pytest.fixture
def load_balancer(mock_config, mock_health_check, mock_server_pool):
    """Fixture to initialize the LoadBalancer with mocked components."""
    with patch("async_flow.health.HealthCheck", return_value=mock_health_check):
        with patch("async_flow.server_pool.ServerPool", return_value=mock_server_pool):
            lb = LoadBalancer(mock_config)
            lb.server_pool = mock_server_pool  # Ensure mock_server_pool is used
            lb.health_check = mock_health_check
            return lb

@pytest.mark.asyncio
async def test_forward_http_request(load_balancer, mock_health_check, mock_server_pool):
    """Test forwarding an HTTP request to a healthy server."""
    # Mock the start_http_server method to not start an actual server
    with patch.object(load_balancer, "start_http_server", new=AsyncMock()):
        await load_balancer.start()

    # Mock aiohttp ClientSession to simulate server response
    with patch("aiohttp.ClientSession.request") as mock_request:
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.headers = {"Content-Type": "text/plain"}
        mock_response.read = AsyncMock(return_value=b"Hello from LoadBalancer!")
        mock_request.return_value.__aenter__.return_value = mock_response

        # Create a mock request
        request = MagicMock(spec=web.Request)
        request.method = "GET"
        request.rel_url = web.URL("/test")
        request.headers = {}
        request.read = AsyncMock(return_value=b"")

        # Call the handle_http_request method directly
        response = await load_balancer.handle_http_request(request)

        # Assertions
        mock_request.assert_called_once_with(
            method="GET",
            url="http://127.0.0.1:9000/test",
            headers={},
            data=b""
        )
        assert response.status == 200
        assert response.text == "Hello from LoadBalancer!"

    await load_balancer.shutdown()
