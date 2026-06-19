import socket
import threading
import os
import mimetypes
from datetime import datetime

HOST = '0.0.0.0'
TCP_PORT = 8000
UDP_PORT = 9000

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

def get_timestamp():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# TCP HTTP SERVER LOGIC
def handle_tcp_client(client_socket, client_address):
    print(f"[{get_timestamp()}] [TCP] Thread created for new connection from {client_address[0]}")
    
    try:
        request = client_socket.recv(4096).decode('utf-8')
        
        if not request:
            return

        request_lines = request.split('\r\n')
        first_line = request_lines[0]
        
        try:
            requested_path = first_line.split(' ')[1]
        except IndexError:
            print(f"[{get_timestamp()}] [TCP] Malformed request received from {client_address[0]}.")
            return

        # Default to index.html
        if requested_path == '/':
            requested_path = '/index.html'

        safe_path = os.path.normpath(requested_path.lstrip('/'))
        target_file = os.path.abspath(os.path.join(BASE_DIR, safe_path))

        try:
            if not target_file.startswith(BASE_DIR):
                print(f"[{get_timestamp()}] [TCP] SECURITY ALERT: Traversal attempt from {client_address[0]}. Routing to 404.")
                raise FileNotFoundError

            if not os.path.isfile(target_file):
                raise FileNotFoundError

            with open(target_file, 'rb') as file:
                file_content = file.read()
            
            # mimetypes
            content_type, _ = mimetypes.guess_type(target_file)
            if not content_type:
                content_type = 'text/html; charset=utf-8'
            elif content_type == 'text/html':
                content_type = 'text/html; charset=utf-8'

            headers = (
                "HTTP/1.1 200 OK\r\n"
                f"Content-Type: {content_type}\r\n"
                f"Content-Length: {len(file_content)}\r\n"
                "Connection: close\r\n\r\n"
            )
            
            client_socket.sendall(headers.encode('utf-8') + file_content)
            print(f"[{get_timestamp()}] [TCP] {client_address[0]} requested {requested_path} - 200 OK")

        except FileNotFoundError:
            print(f"[{get_timestamp()}] [TCP] {client_address[0]} requested {requested_path} - 404 Not Found")
            
            # 1. Try to read the actual 404.html file
            try:
                error_file_path = os.path.join(BASE_DIR, 'status', '404.html')
                with open(error_file_path, 'rb') as f:
                    error_body = f.read()
            except FileNotFoundError:
                # 2. Emergency Fallback
                error_body = b"<h1>404 - File Not Found</h1><p>Check your URL and try again.</p>"
                
            error_headers = (
                "HTTP/1.1 404 Not Found\r\n"
                "Content-Type: text/html; charset=utf-8\r\n"
                f"Content-Length: {len(error_body)}\r\n"
                "Connection: close\r\n\r\n"
            ).encode('utf-8')
            
            client_socket.sendall(error_headers + error_body)

    except Exception as e:
        print(f"[{get_timestamp()}] [TCP] Error with client {client_address[0]}: {e}")
        try:
            # 1. Try to read the actual 500.html file
            try:
                error_file_path = os.path.join(BASE_DIR, 'status', '500.html')
                with open(error_file_path, 'rb') as f:
                    error_body = f.read()
            except FileNotFoundError:
                # 2. Emergency Fallback
                error_body = b"<h1>500 - Internal Server Error</h1><p>Something went wrong on the server.</p>"
                
            error_headers = (
                "HTTP/1.1 500 Internal Server Error\r\n"
                "Content-Type: text/html; charset=utf-8\r\n"
                f"Content-Length: {len(error_body)}\r\n"
                "Connection: close\r\n\r\n"
            ).encode('utf-8')
            
            client_socket.sendall(error_headers + error_body)
            
        except Exception as send_error:
            print(f"[{get_timestamp()}] [TCP] Failed to send 500 response to {client_address[0]}: {send_error}")
    
    finally:
        client_socket.close()
        print(f"[{get_timestamp()}] [TCP] Connection closed for {client_address[0]}")

def start_tcp_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, TCP_PORT))
    server_socket.listen(5)
    
    while True:
        client_socket, client_address = server_socket.accept()
        client_thread = threading.Thread(target=handle_tcp_client, args=(client_socket, client_address))
        client_thread.start()

def start_udp_server():
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind((HOST, UDP_PORT))
    
    while True:
        try:
            data, client_address = udp_socket.recvfrom(1024)
            if data:
                print(f"[{get_timestamp()}] [UDP] Echoed packet back to {client_address[0]}")
                udp_socket.sendto(data, client_address)
        except Exception as e:
            print(f"[{get_timestamp()}] [UDP] Error: {e}")

if __name__ == "__main__":
    print(f"[{get_timestamp()}] [*] Server running on port {TCP_PORT}/{UDP_PORT}")
    print(f"[{get_timestamp()}] [*] Serving files from: {BASE_DIR}")

    tcp_thread = threading.Thread(target=start_tcp_server)
    tcp_thread.daemon = True
    tcp_thread.start()

    udp_thread = threading.Thread(target=start_udp_server)
    udp_thread.daemon = True
    udp_thread.start()

    try:
        while True:
            pass
    except KeyboardInterrupt:
        print(f"\n[{get_timestamp()}] [*] Shutting down servers.")