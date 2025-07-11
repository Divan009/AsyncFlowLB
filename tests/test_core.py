import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from async_flow.core import LoadBalancer
from async_flow.models.config import LoadBalancerConfig
import pytest
import asyncio
from unittest.mock import AsyncMock, patch


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
            "interval": 10,
            "timeout": 5,
            "path": "/health",
            "retries": 3
        },
        load_balance={
            "algorithms": "round_robin",
            "servers": [
                {"host": "127.0.0.1", "port": 9000, "weight": 1}
            ]
        }
    )


@pytest.fixture
def mock_health_check():
    """Fixture to mock the HealthCheck object."""
    return AsyncMock()


@pytest.fixture
def mock_server_pool():
    """Fixture to mock the ServerPool object."""
    return MagicMock()


@pytest.fixture
def load_balancer(mock_config, mock_health_check, mock_server_pool):
    """Fixture to initialize the LoadBalancer with mocked components."""
    with patch("async_flow.health.HealthCheck", return_value=mock_health_check):
        with patch("async_flow.server_pool.ServerPool", return_value=mock_server_pool):
            lb = LoadBalancer(mock_config)
            lb.health_check = mock_health_check  # Explicitly assign the mock
            return lb


@pytest.mark.skip(reason="Not implemented yet")
@pytest.mark.asyncio
async def test_load_balancer_start_http(load_balancer, mock_health_check):
    """Test that the LoadBalancer starts the HTTP server with a timeout."""
    # Mock the start_http_server method
    with patch.object(load_balancer, "start_http_server", new=AsyncMock()) as mock_start_http:
        try:
            # Add a timeout to the `await` call for `load_balancer.start()`
            await asyncio.wait_for(load_balancer.start(), timeout=5)

            # Assert that health checks are started
            mock_health_check.start.assert_called_once()

            # Assert that the HTTP server was started
            mock_start_http.assert_called_once()
        except asyncio.TimeoutError:
            pytest.fail("The test timed out while starting the LoadBalancer.")


@pytest.mark.skip(reason="Not implemented yet")
@pytest.mark.asyncio
async def test_load_balancer_start_tcp(load_balancer, mock_health_check, mock_config):
    """Test that the LoadBalancer starts the TCP server."""
    # Change protocol to TCP
    mock_config.listen.protocol = "tcp"

    # Mock the start_tcp_server method
    with patch.object(load_balancer, "start_tcp_server", new=AsyncMock()) as mock_start_tcp:
        await load_balancer.start()

        # Assert that health checks are started
        mock_health_check.start.assert_called_once()

        # Assert that the TCP server was started
        mock_start_tcp.assert_called_once()


@pytest.mark.asyncio
async def test_load_balancer_unsupported_protocol(load_balancer, mock_config):
    """Test that the LoadBalancer handles unsupported protocol_health_check."""
    # Set an unsupported protocol
    mock_config.listen.protocol = "udp"

    with pytest.raises(ValueError, match="Unsupported protocol"):
        await load_balancer.start()


@pytest.mark.asyncio
async def test_load_balancer_shutdown(load_balancer, mock_health_check):
    """Test that the LoadBalancer shuts down gracefully."""
    with patch.object(load_balancer.logger, "info") as mock_logger:
        await load_balancer.shutdown()

        # Assert that health checks are stopped
        mock_health_check.close.assert_called_once()

        # Check logs
        mock_logger.assert_any_call("Initiating LoadBalancer shutdown...")
        mock_logger.assert_any_call("LoadBalancer shutdown completed.")
