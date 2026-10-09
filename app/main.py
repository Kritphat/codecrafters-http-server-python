import socket


def handle(conn):

    data = conn.recv(1024)
    text = data.decode()

    request_line = text.split("\r\n")[0]
    parts = request_line.split()
    path = parts[1] if len(parts) > 1 else ""

    
    part_path = path.split("/")
    first_path = part_path[1]
    sec_path = part_path[2] if len(part_path) > 2 else ""


    if path == "/":                                   
        conn.sendall(b"HTTP/1.1 200 OK\r\n\r\n")
    elif first_path == "echo" and sec_path != "":   
        response = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/plain\r\n"
            f"Content-Length: {len(sec_path.encode())}\r\n"
            "\r\n"
            f"{sec_path}"
        )
        conn.sendall(response.encode())
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
