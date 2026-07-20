import socket

from ui import build_interface


def find_free_port(start_port=3000, attempts=20):
    for port in range(start_port, start_port + attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            if sock.connect_ex(("127.0.0.1", port)) != 0:
                return port

    raise RuntimeError(f"No free port found from {start_port} to {start_port + attempts - 1}.")


demo = build_interface()


if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=find_free_port())
