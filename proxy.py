import socket
import threading
import os

HOST = '0.0.0.0'
PROXY_PORT = 8080
WEBSERVER_HOST = '127.0.0.1' 
WEBSERVER_PORT = 8000

def handle_client(client_socket, client_address):
    print(f"\n[PROXY] Connection received from {client_address}")
    
    try:
        request = client_socket.recv(4096)
        if not request:
            return
            
        print(f"[PROXY] Forwarding request for {client_address[0]}...")

        try:
            request_str = request.decode('utf-8')
            requested_path = request_str.split('\r\n')[0].split(' ')[1]
            if requested_path == '/':
                requested_path = '/index.html'
                
            cache_filename = "cache/" + requested_path.replace('/', '_')

            if os.path.exists(cache_filename):
                print(f"[PROXY] Cache HIT for {requested_path}")
                with open(cache_filename, 'rb') as f:
                    cached_data = f.read()

                client_socket.sendall(cached_data)
                return 
                
            else:
                print(f"[PROXY] Cache MISS for {requested_path}. Fetching from server...")
                
        except Exception as e:
            print(f"[PROXY] Request parsing error: {e}")

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.connect((WEBSERVER_HOST, WEBSERVER_PORT))
        
        server_socket.sendall(request)
        
        response = b""
        while True:
            chunk = server_socket.recv(4096)
            if len(chunk) > 0:
                response += chunk
            else:
                break
                
        if not os.path.exists('cache'):
            os.makedirs('cache')
            
        with open(cache_filename, 'wb') as f:
            f.write(response)
            
        print(f"[PROXY] Stored {requested_path} in cache.")
        
        client_socket.sendall(response)
        print("[PROXY] Successfully forwarded response to browser.")

    except ConnectionRefusedError:
        print("[PROXY] ERROR: Web server is down! Sending 502 Bad Gateway.")
        error_body = "<h1>502 Bad Gateway</h1><p>The web server is offline.</p>"
        error_msg = (
            "HTTP/1.1 502 Bad Gateway\r\n"
            "Content-Type: text/html; charset=utf-8\r\n"
            f"Content-Length: {len(error_body.encode('utf-8'))}\r\n"
            "Connection: close\r\n\r\n"
        )
        client_socket.sendall((error_msg + error_body).encode('utf-8'))

    except Exception as e:
        print(f"[PROXY] General Error: {e}")
        
    finally:
        client_socket.close()
        try:
            server_socket.close()
        except:
            pass

def start_proxy():
    proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    proxy_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    proxy_socket.bind((HOST, PROXY_PORT))
    proxy_socket.listen(5)
    
    print(f"[*] Proxy Server listening on {HOST}:{PROXY_PORT}")
    
    while True:
        client_socket, client_address = proxy_socket.accept()
        thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        thread.daemon = True
        thread.start()

if __name__ == "__main__":
    start_proxy()