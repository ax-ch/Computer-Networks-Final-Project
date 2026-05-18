import socket
import threading

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

        # -------------------------------------------------------------
        # TODO for later: Check if request is already in our local cache!
        # -------------------------------------------------------------

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
                
        # -------------------------------------------------------------
        # TODO for later: Save 'response' to a local cache file
        # -------------------------------------------------------------
        
        client_socket.sendall(response)
        print("[PROXY] Successfully forwarded response to browser.")

    except ConnectionRefusedError:
        print("[PROXY] ERROR: Web server is down! Sending 502 Bad Gateway.")
        error_msg = "HTTP/1.1 502 Bad Gateway\r\nConnection: close\r\n\r\n<h1>502 Bad Gateway</h1>"
        client_socket.sendall(error_msg.encode('utf-8'))

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