import sys

import yaml
import toml
import json
from pydantic import ValidationError

from async_flow.models.config import LoadBalancerConfig


class Config:
    def __init__(self, target_file: str, is_yaml: bool = False, is_json=False, is_toml=False):
        self.config = None
        self.file = target_file
        self.is_yaml = is_yaml
        self.is_json = is_json
        self.is_toml = is_toml

        if self.is_yaml:
            self.loadYamlConfig()
        elif self.is_json:
            self.loadJsonConfig()
        elif self.is_toml:
            self.loadTomlConfig()
        else:
            raise Exception("Please choose between yaml or json or toml")

        # Validate the loaded configuration
        self.validate_config()

    def reload_config(self):
        """Reload and validate the configuration."""
        if self.is_yaml:
            self.loadYamlConfig()
        elif self.is_json:
            self.loadJsonConfig()
        elif self.is_toml:
            self.loadTomlConfig()
        else:
            self.error_exit("Please specify the configuration file type: YAML, JSON, or TOML.")

        self.validate_config()
        # self.logger.info("Configuration reloaded successfully.")

    def loadYamlConfig(self):
        with open(self.file, 'r') as f:
            self.raw_config = yaml.safe_load(f)
        print(self.config)

    def loadJsonConfig(self):
        with open(self.file, 'r') as f:
            self.raw_config = json.load(f)
        print(self.config)

    def loadTomlConfig(self):
        with open(self.file, 'r') as f:
            self.raw_config = toml.load(f)
        print(self.config)

    def validate_config(self):
        if not hasattr(self, 'raw_config') or self.raw_config is None:
            raise Exception("No configuration found")

        try:
            self.config = LoadBalancerConfig(**self.raw_config)
            # self.logger.info("Configuration validated and parsed successfully.")
        except ValidationError as e:
            raise Exception(f"Configuration validation error:\n{e}")

    def error_exit(self, message: str):
        """Log an error message and exit the program."""
        # self.logger.error(message)
        sys.exit(1)

    def get_config(self) -> LoadBalancerConfig:
        """Return the loaded and validated configuration."""
        return self.config
