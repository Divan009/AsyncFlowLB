import pytest

from async_flow.config import Config


def test_valid_yaml_config():
    # Path to a valid configuration file
    config_path = 'examples/config.yaml'

    # Initialize the Config class with YAML
    config_loader = Config(target_file=config_path, is_yaml=True)
    config = config_loader.get_config()

    # Assertions to verify correct loading and validation
    assert config.listen.host == "0.0.0.0"
    assert config.listen.port == 8080
    assert config.load_balance.algorithms == "round_robin"
    assert len(config.load_balance.servers) == 3
    assert config.load_balance.servers[0].host == "127.0.0.1"
    assert config.load_balance.servers[0].port == 60001
    assert config.load_balance.servers[0].weight == 1
    assert config.health_check.interval == 10
    assert config.health_check.timeout == 2
    # 'retries' is optional; check if it's set or None
    assert config.health_check.retries is None or config.health_check.retries == 3
    assert config.health_check.path == "/health"


def test_missing_weight():
    config_path = 'examples/invalid_config_missing_weight.yaml'

    with pytest.raises(Exception) as excinfo:
        Config(target_file=config_path, is_yaml=True)

    assert "Configuration validation error" in str(excinfo.value)


def test_invalid_health_check():
    config_path = 'examples/invalid_config_health_check.yaml'

    with pytest.raises(Exception) as excinfo:
        Config(target_file=config_path, is_yaml=True)

    assert "Configuration validation error" in str(excinfo.value)