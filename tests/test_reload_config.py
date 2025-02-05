import pytest
import tempfile
import os
import yaml
from async_flow.config import Config

def test_valid_yaml_config():
    # Create a temporary YAML file with valid configuration
    valid_config = {
        "listen": {
            "host": "0.0.0.0",
            "port": 8080,
            "protocol": "http"
        },
        "load_balance": {
            "algorithms": "round_robin",
            "servers": [
                {"host": "192.168.1.10", "port": 5000, "weight": 1},
                {"host": "192.168.1.11", "port": 5000, "weight": 2},
                {"host": "192.168.1.12", "port": 5000, "weight": 1}
            ]
        },
        "health_check": {
            "interval": 10,
            "timeout": 2,
            "path": "/health",
            "retries": 3
        }
    }

    with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.yaml') as tmp:
        yaml.dump(valid_config, tmp)
        tmp_path = tmp.name

    try:
        config_loader = Config(target_file=tmp_path, is_yaml=True)
        config = config_loader.get_config()
        assert config.listen.host == "0.0.0.0"
        assert config.listen.port == 8080
        assert config.listen.protocol == "http"
        assert config.load_balance.algorithms == "round_robin"
        assert len(config.load_balance.servers) == 3
        assert config.health_check.retries == 3
    finally:
        os.remove(tmp_path)

def test_reload_config_valid():
    # Initial valid config
    initial_config = {
        "listen": {
            "host": "127.0.0.1",
            "port": 8000,
            "protocol": "http"
        },
        "load_balance": {
            "algorithms": "least_connections",
            "servers": [
                {"host": "192.168.1.20", "port": 6000, "weight": 1},
                {"host": "192.168.1.21", "port": 6000, "weight": 2}
            ]
        },
        "health_check": {
            "interval": 15,
            "timeout": 3,
            "path": "/status",
            "retries": 5
        }
    }

    # Updated config
    updated_config = {
        "listen": {
            "host": "0.0.0.0",
            "port": 9000,
            "protocol": "http"
        },
        "load_balance": {
            "algorithms": "round_robin",
            "servers": [
                {"host": "192.168.1.30", "port": 7000, "weight": 3},
                {"host": "192.168.1.31", "port": 7000, "weight": 4}
            ]
        },
        "health_check": {
            "interval": 20,
            "timeout": 4,
            "path": "/healthz",
            "retries": 6
        }
    }

    with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.yaml') as tmp:
        yaml.dump(initial_config, tmp)
        tmp_path = tmp.name

    try:
        config_loader = Config(target_file=tmp_path, is_yaml=True)
        config = config_loader.get_config()
        assert config.listen.host == "127.0.0.1"
        assert config.listen.port == 8000
        assert config.load_balance.algorithms == "least_connections"
        assert len(config.load_balance.servers) == 2
        assert config.health_check.retries == 5

        # Update the YAML file with new config
        with open(tmp_path, 'w') as f:
            yaml.dump(updated_config, f)

        # Reload the configuration
        config_loader.reload_config()
        updated_config_loaded = config_loader.get_config()

        # Assertions to verify the updated configuration
        assert updated_config_loaded.listen.host == "0.0.0.0"
        assert updated_config_loaded.listen.port == 9000
        assert updated_config_loaded.load_balance.algorithms == "round_robin"
        assert len(updated_config_loaded.load_balance.servers) == 2
        assert updated_config_loaded.load_balance.servers[0].host == "192.168.1.30"
        assert updated_config_loaded.load_balance.servers[0].port == 7000
        assert updated_config_loaded.load_balance.servers[0].weight == 3
        assert updated_config_loaded.health_check.interval == 20
        assert updated_config_loaded.health_check.timeout == 4
        assert updated_config_loaded.health_check.path == "/healthz"
        assert updated_config_loaded.health_check.retries == 6

    finally:
        os.remove(tmp_path)

def test_reload_config_invalid():
    # Initial valid config
    initial_config = {
        "listen": {
            "host": "127.0.0.1",
            "port": 8000,
            "protocol": "http"
        },
        "load_balance": {
            "algorithms": "least_connections",
            "servers": [
                {"host": "192.168.1.20", "port": 6000, "weight": 1},
                {"host": "192.168.1.21", "port": 6000, "weight": 2}
            ]
        },
        "health_check": {
            "interval": 15,
            "timeout": 3,
            "path": "/status",
            "retries": 5
        }
    }

    # Invalid updated config (missing 'weight' and invalid 'path')
    invalid_updated_config = {
        "listen": {
            "host": "0.0.0.0",
            "port": 9000,
            "protocol": "http"
        },
        "load_balance": {
            "algorithms": "least_connections",
            "servers": [
                {"host": "192.168.1.30", "port": 7000},  # Missing 'weight'
                {"host": "192.168.1.31", "port": 7000, "weight": 4}
            ]
        },
        "health_check": {
            "interval": -20,  # Invalid: negative
            "timeout": 0,     # Invalid: zero
            "path": "healthz",  # Invalid: does not start with '/'
            "retries": 6
        }
    }

    with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.yaml') as tmp:
        yaml.dump(initial_config, tmp)
        tmp_path = tmp.name

    try:
        config_loader = Config(target_file=tmp_path, is_yaml=True)
        config = config_loader.get_config()
        assert config.listen.host == "127.0.0.1"
        assert config.listen.port == 8000

        # Update the YAML file with invalid config
        with open(tmp_path, 'w') as f:
            yaml.dump(invalid_updated_config, f)

        # Attempt to reload the configuration and expect an Exception
        with pytest.raises(Exception) as excinfo:
            config_loader.reload_config()

        assert "Configuration validation error" in str(excinfo.value)

    finally:
        os.remove(tmp_path)
