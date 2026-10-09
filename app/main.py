import socket


def handle(conn):
    data = conn.recv(1024)
    text = data.decode()

    request_line = text.split("\r\n")[0]
    parts = request_line.split()
    path = parts[1] if len(parts) > 1 else ""

    if path in ("/", "/index.html"):
        conn.sendall(b"HTTP/1.1 200 OK\r\n\r\n")
    else:
        conn.sendall(b"HTTP/1.1 404 Not Found\r\n\r\n")

    conn.close()


def main():
    print("Logs from your program will appear here!")
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    conn, addr = server_socket.accept()
    handle(conn)


if __name__ == "__main__":
    main()
