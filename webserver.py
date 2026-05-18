import socket
import threading
import os

HOST = '0.0.0.0' # listen on all available LAN/WiFi
TCP_PORT = 8000
UDP_PORT = 9000

# TCP HTTP SERVER LOGIC
def handle_tcp_client(client_socket, client_address):
    print(f"[TCP] New connection from {client_address}")
    
    try:
        request = client_socket.recv(4096).decode('utf-8')
        
        if not request:
            return

        print(f"[TCP] Request received:\n{request}")

        request_lines = request.split('\r\n')
        first_line = request_lines[0]
        
        try:
            requested_path = first_line.split(' ')[1]
        except IndexError:
            print("[TCP] Malformed request received.")
            return

        if requested_path == '/':
            file_name = 'index.html'
        else:
            file_name = requested_path.lstrip('/') 

        try:
            # 'rb' means Read Binary
            with open(file_name, 'rb') as file:
                file_content = file.read()
            
            headers = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: text/html; charset=utf-8\r\n"
                f"Content-Length: {len(file_content)}\r\n"
                "Connection: close\r\n\r\n"
            )
            
            client_socket.sendall(headers.encode('utf-8') + file_content)
            
            print(f"[TCP] {client_address[0]} requested {requested_path} - 200 OK")

        except FileNotFoundError:
            print(f"[TCP] {client_address[0]} requested {requested_path} - 404 Not Found")
            
            error_body = "<h1>404 - File Not Found</h1><p>Check your URL and try again.</p>"
            
            error_headers = (
                "HTTP/1.1 404 Not Found\r\n"
                "Content-Type: text/html; charset=utf-8\r\n"
                f"Content-Length: {len(error_body.encode('utf-8'))}\r\n"
                "Connection: close\r\n\r\n"
            )

            client_socket.sendall((error_headers + error_body).encode('utf-8'))

    except Exception as e:
        print(f"[TCP] Error with client {client_address}: {e}")
    
    finally:
        client_socket.close()
        print(f"[TCP] Connection closed for {client_address}")


def start_tcp_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    server_socket.bind((HOST, TCP_PORT))
    server_socket.listen(5)
    
    print(f"[*] TCP Server (HTTP) listening on {HOST}:{TCP_PORT}")
    
    while True:
        client_socket, client_address = server_socket.accept()
        
        client_thread = threading.Thread(target=handle_tcp_client, args=(client_socket, client_address))
        client_thread.start()


# UDP ECHO SERVER LOGIC
def start_udp_server():
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind((HOST, UDP_PORT))
    
    print(f"[*] UDP Server (Echo) listening on {HOST}:{UDP_PORT}")
    
    while True:
        try:
            data, client_address = udp_socket.recvfrom(1024)

            if data:
                udp_socket.sendto(data, client_address)
                
        except Exception as e:
            print(f"[UDP] Error: {e}")


# MAIN
if __name__ == "__main__":
    print("[*] Starting Web Server processes...")

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
        print("\n[*] Shutting down servers.")