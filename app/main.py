import socket
import threading
import os
import sys
import gzip


directory = ""

def process_request(conn, data):
    text = data.decode()
    body = data.split(b"\r\n\r\n", 1)[1] if b"\r\n\r\n" in data else b""

    lines = text.split("\r\n")
    request_line = lines[0]

    parts = request_line.split()
    method = parts[0] if len(parts) > 0 else ""
    path = parts[1] if len(parts) > 1 else ""
    
    headers = {}
    for line in lines[1:]:
        if line == "":                                # empty line = end of headers
            break
        name, value = line.split(":", 1)              # split only at the first ":"
        headers[name.strip().lower()] = value.strip()

    close = headers.get("connection", "").lower() == "close"
    
    part_path = path.split("/")
    first_path = part_path[1] if len(part_path) > 1 else ""
    sec_path = part_path[2] if len(part_path) > 2 else ""


    if path == "/":
        send(conn, b"HTTP/1.1 200 OK\r\n\r\n", close)

    elif first_path == "echo" and sec_path != "":
        echo_body = sec_path.encode()
        accept_encoding = headers.get("accept-encoding", "")
        encodings = [e.strip() for e in accept_encoding.split(",")]

        if "gzip" in encodings:
            echo_body = gzip.compress(echo_body)
            response = (
                b"HTTP/1.1 200 OK\r\n"
                b"Content-Type: text/plain\r\n"
                b"Content-Encoding: gzip\r\n"
                + f"Content-Length: {len(echo_body)}\r\n".encode()
                + b"\r\n"
                + echo_body
            )
        else:
            response = (
                b"HTTP/1.1 200 OK\r\n"
                b"Content-Type: text/plain\r\n"
                + f"Content-Length: {len(echo_body)}\r\n".encode()
                + b"\r\n"
                + echo_body
            )
        send(conn, response, close)

    elif path == "/user-agent":
        user_agent = headers.get("user-agent", "")
        response = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/plain\r\n"
            f"Content-Length: {len(user_agent.encode())}\r\n"
            "\r\n"
            f"{user_agent}"
        )
        send(conn, response.encode(), close)

    elif first_path == "files" and sec_path != "":
        file_path = os.path.join(directory, sec_path)

        if method == "POST":  
            with open(file_path, "wb") as f:
                f.write(body)
            send(conn, b"HTTP/1.1 201 Created\r\n\r\n", close)
        elif os.path.isfile(file_path):
            with open(file_path, "rb") as f:
                content = f.read()
            header = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: application/octet-stream\r\n"
                f"Content-Length: {len(content)}\r\n"
                "\r\n"
            )
            send(conn, header.encode() + content, close)
        else:
            send(conn, b"HTTP/1.1 404 Not Found\r\n\r\n", close)


    else:
        send(conn, b"HTTP/1.1 404 Not Found\r\n\r\n", close)


    return close

def handle(conn):
    while True:
        data = conn.recv(1024)
        if not data:
            break

        close = process_request(conn, data)

        if close:
            break

    conn.close()


def send(conn, response, close):
    if close:
        # insert the header right after the status line
        status_line, rest = response.split(b"\r\n", 1)
        response = status_line + b"\r\nConnection: close\r\n" + rest
    conn.sendall(response)




def main():
    global directory
    if "--directory" in sys.argv:
        directory = sys.argv[sys.argv.index("--directory") + 1]


    print("Logs from your program will appear here!")
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    while True:
        conn, addr = server_socket.accept()
        worker = threading.Thread(target=handle, args=(conn,))
        worker.start()


if __name__ == "__main__":
    main()
