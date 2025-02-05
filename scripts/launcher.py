# scripts/launch_servers.py

import subprocess
import sys
import os

def launch_server(host, port):
    """Launch a server instance as a subprocess."""
    script_path = os.path.join(os.path.dirname(__file__), 'server.py')
    return subprocess.Popen(
        [sys.executable, script_path, '--host', host, '--port', str(port)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

def main():
    """Main function to launch and manage multiple server instances."""
    servers = [
        {'host': '127.0.0.1', 'port': 60001},
        {'host': '127.0.0.1', 'port': 60002},
        {'host': '127.0.0.1', 'port': 60003},
    ]

    processes = []
    try:
        for server in servers:
            print(f"Launching server at {server['host']}:{server['port']}")
            process = launch_server(server['host'], server['port'])
            processes.append(process)

        # Continuously read and print server outputs
        while True:
            for process in processes:
                stdout, stderr = process.communicate(timeout=1)
                if stdout:
                    print(stdout.decode().strip())
                if stderr:
                    print(stderr.decode().strip())
    except KeyboardInterrupt:
        print("\nShutting down all servers...")
        for process in processes:
            process.terminate()
        for process in processes:
            process.wait()
        print("All servers have been shut down.")
    except subprocess.TimeoutExpired:
        pass
    except Exception as e:
        print(f"An error occurred: {e}")
        for process in processes:
            process.terminate()
        for process in processes:
            process.wait()
    finally:
        print("Exiting.")

if __name__ == '__main__':
    main()
