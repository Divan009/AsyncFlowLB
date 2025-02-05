# scripts/server.py

import argparse
from aiohttp import web
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Server")

async def handle_health(request):
    """Health check endpoint."""
    logger.info(f"Health check received from {request.remote}")
    return web.Response(text="OK", status=200)

async def handle_root(request):
    """Root endpoint."""
    logger.info(f"Received request from {request.remote}")
    return web.Response(text="Hello from Server!", status=200)

def create_app():
    """Create and configure the aiohttp application."""
    app = web.Application()
    app.router.add_get('/health', handle_health)
    app.router.add_route('*', '/{tail:.*}', handle_root)
    return app

def main():
    """Parse arguments and run the server."""
    parser = argparse.ArgumentParser(description="Simple AIOHTTP Server")
    parser.add_argument('--host', type=str, required=True, help='Host IP address to bind (e.g., 192.168.1.10)')
    parser.add_argument('--port', type=int, required=True, help='Port number to bind (e.g., 5000)')
    args = parser.parse_args()

    app = create_app()
    logger.info(f"Starting server at {args.host}:{args.port}")
    web.run_app(app, host=args.host, port=args.port)

if __name__ == '__main__':
    main()
