import asyncio
from typing import Dict, Callable, Coroutine, Any

import aiohttp
from aiohttp import web
from async_flow.logger import get_logger
from async_flow.health import HealthCheck
from async_flow.models.config import LoadBalancerConfig
from async_flow.server_pool import ServerPool

from src.async_flow.algorithms.base_algorithm import AlgorithmFactory, AlgorithmContext


class LoadBalancer:
    def __init__(self, config: LoadBalancerConfig):
        self.config = config
        self.server_pool = ServerPool(config.load_balance.servers)
        self.health_check = HealthCheck(
            server_pool=self.server_pool,
            config=config.health_check,
            protocol=config.listen.protocol
        )
        self.logger = get_logger(self.__class__.__name__)

        self.server_startup_methods: Dict[str, Callable[[], Coroutine[Any, Any, None]]] = {
            'http': self.start_http_server,
            'tcp': self.start_tcp_server
        }

        algorithm_factory = AlgorithmFactory()
        self.algorithm = algorithm_factory.build(algorithm_type=config.load_balance.algorithms)
        self.algorithm_context = AlgorithmContext(algorithm=self.algorithm)

    async def start(self):
        """Start the load balancer components."""
        await self.health_check.start()

        protocol = self.config.listen.protocol.lower()
        startup_method = self.server_startup_methods.get(protocol)

        if startup_method:
            try:
                await startup_method()
                self.logger.info("LoadBalancer started.")
            except Exception as e:
                self.logger.error(f"Failed to start {protocol.upper()} server: {e}")
                await self.shutdown()  # Ensure graceful shutdown on failure
                raise
        else:
            self.logger.error(f"Unsupported protocol: {self.config.listen.protocol}")
            raise ValueError(f"Unsupported protocol: {self.config.listen.protocol}")

    async def handle_http_request(self, request: web.Request) -> web.Response:
        # Implement your request handling logic here

        healthy_servers = self.server_pool.get_healthy_servers()
        if not healthy_servers:
            self.logger.error("No healthy servers available to handle the request.")
            return web.Response(status=503, text="Service Unavailable")

        selected_server = self.algorithm_context.execute(server_list=healthy_servers)
        self.logger.info(f"Forwarding HTTP request to: {selected_server['host']}:{selected_server['port']}")

        # Construct the target URL
        target_url = f"http://{selected_server['host']}:{selected_server['port']}{request.rel_url}"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(
                        method=request.method,
                        url=target_url,
                        headers=request.headers,
                        data=await request.read()
                ) as resp:
                    response_text = await resp.read()
                    return web.Response(
                        status=resp.status,
                        headers=resp.headers,
                        body=response_text
                    )
        except Exception as e:
            self.logger.error(f"Error forwarding HTTP request to {selected_server}: {e}")
            return web.Response(status=502, text="Bad Gateway")


    async def start_http_server(self):
        """Initialize and start the HTTP server."""
        app = web.Application()
        app.router.add_route('*', '/', self.handle_http_request)
        app.router.add_route('*', '/{tail:.*}', self.handle_http_request)
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, self.config.listen.host, self.config.listen.port)
        await site.start()
        self.logger.info(f"HTTP server listening on {self.config.listen.host}:{self.config.listen.port}")


    async def handle_tcp_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """
        Handle incoming TCP connections by forwarding data to a healthy server.
        """
        healthy_servers = self.server_pool.get_healthy_servers()
        if not healthy_servers:
            self.logger.error("No healthy servers available to handle the TCP connection.")
            writer.close()
            await writer.wait_closed()
            return

        selected_server = self.algorithm_context.execute(server_list=healthy_servers)
        self.logger.info(f"Forwarding TCP connection to: {selected_server['host']}:{selected_server['port']}")

        try:
            # Connect to the selected server
            remote_reader, remote_writer = await asyncio.open_connection(
                selected_server['host'], selected_server['port']
            )

            async def relay(reader_stream: asyncio.StreamReader, writer_stream: asyncio.StreamWriter):
                try:
                    while True:
                        data = await reader_stream.read(4096)
                        if not data:
                            break
                        writer_stream.write(data)
                        await writer_stream.drain()
                except Exception as e:
                    self.logger.error(f"Error relaying data: {e}")
                finally:
                    writer_stream.close()

            # Start relaying data between client and server
            await asyncio.gather(
                relay(reader, remote_writer),
                relay(remote_reader, writer)
            )
        except Exception as e:
            self.logger.error(f"Error forwarding TCP connection to {selected_server}: {e}")
            writer.close()
            await writer.wait_closed()


    async def start_tcp_server(self):
        """Initialize and start the TCP server."""

        server = await asyncio.start_server(
            self.handle_tcp_client,
            self.config.listen.host,
            self.config.listen.port
        )
        addr = server.sockets[0].getsockname()
        self.logger.info(f"TCP server listening on {addr}")

        async with server:
            await server.serve_forever()

    async def shutdown(self):
        """Gracefully shutdown the load balancer."""
        self.logger.info("Initiating LoadBalancer shutdown...")
        await self.health_check.close()
        self.logger.info("LoadBalancer shutdown completed.")