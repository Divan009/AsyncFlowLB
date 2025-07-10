import asyncio
import sys

from src.async_flow.logger import setup_logging
from src.async_flow.core import LoadBalancer
from src.async_flow.config import Config


def main():
    # Setup centralized logging
    setup_logging(
        log_level="INFO",
        log_format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        date_format="%Y-%m-%d %H:%M:%S",
        log_dir="logs",
        log_file="loadbalancer.log",
        max_bytes=10 ** 6,
        backup_count=5
    )

    import logging
    logger = logging.getLogger("Main")

    import argparse

    parser = argparse.ArgumentParser(description="Stealth PAWS is a load balancer written in Python")
    parser.add_argument('--config', type=str, required=True, help='Path to the configuration file')
    parser.add_argument('--type', type=str, required=True, choices=['yaml', 'json', 'toml'], help='Configuration file type')
    args = parser.parse_args()

    is_yaml = args.type.lower() == 'yaml'
    is_json = args.type.lower() == 'json'
    is_toml = args.type.lower() == 'toml'

    config_loader = Config(
        target_file=args.config,
        is_yaml=is_yaml,
        is_json=is_json,
        is_toml=is_toml
    )

    try:
        config = config_loader.get_config()
        logger.info(f"succesfully loaded configuration")
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        sys.exit(1)

    print(config)

    # Initialize and start LoadBalancer
    load_balancer = LoadBalancer(config)
    try:
        asyncio.run(load_balancer.start())
    except KeyboardInterrupt:
        logger.info("LoadBalancer shutdown initiated by user.")
    except Exception as e:
        logger.exception(f"LoadBalancer encountered an error: {e}")
    finally:
        load_balancer.shutdown()



if __name__ == "__main__":
    main()