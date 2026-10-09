import socket
import threading
import os
import sys

directory = ""

def handle(conn):

    data = conn.recv(1024)
    text = data.decode()

    lines = text.split("\r\n")
    request_line = lines[0]
    parts = request_line.split()
    path = parts[1] if len(parts) > 1 else ""
    
    headers = {}
    for line in lines[1:]:
        if line == "":                                # empty line = end of headers
            break
        name, value = line.split(":", 1)              # split only at the first ":"
        headers[name.strip().lower()] = value.strip()
    
    part_path = path.split("/")
    first_path = part_path[1] if len(part_path) > 1 else ""
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

    elif path == "/user-agent":                       
        user_agent = headers.get("user-agent", "")
        response = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/plain\r\n"
            f"Content-Length: {len(user_agent.encode())}\r\n"
            "\r\n"
            f"{user_agent}"
        )
        conn.sendall(response.encode())
    
    elif first_path == "files" and sec_path != "":  
        file_path = os.path.join(directory, sec_path)
        if os.path.isfile(file_path):
            with open(file_path, "rb") as f:          #read byte in file
                content = f.read()
            header = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: application/octet-stream\r\n"
                f"Content-Length: {len(content)}\r\n"
                "\r\n"
            )
            conn.sendall(header.encode() + content)
        else:
            conn.sendall(b"HTTP/1.1 404 Not Found\r\n\r\n")

    else:
        conn.sendall(b"HTTP/1.1 404 Not Found\r\n\r\n")

    conn.close()



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
