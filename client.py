import socket
import argparse
import time

# --- Network Configuration ---
PROXY_IP = '127.0.0.1'
PROXY_PORT = 8080
WEBSERVER_IP = '127.0.0.1'
WEBSERVER_PORT = 9000
BUFFER_SIZE = 4096

def run_tcp_mode(filename):
    """
    Phase 1: TCP Mode (HTTP Client)
    Sends a GET request to the Proxy Server and prints the response.
    """
    print(f"[*] Starting TCP Mode. Requesting '{filename}' via Proxy ({PROXY_IP}:{PROXY_PORT})...\n")
    
    # Initialize TCP socket (SOCK_STREAM)
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        # Connect to the proxy
        client_socket.connect((PROXY_IP, PROXY_PORT))
        
        # Construct standard HTTP/1.1 GET request
        # Note: The double CRLF (\r\n\r\n) is mandatory to signal the end of the HTTP header
        request = f"GET {filename} HTTP/1.1\r\nHost: {PROXY_IP}:{PROXY_PORT}\r\nConnection: close\r\n\r\n"
        
        # Send the encoded request
        client_socket.sendall(request.encode('utf-8'))
        
        # Receive the response in chunks
        response = b""
        while True:
            data = client_socket.recv(BUFFER_SIZE)
            if not data:
                break
            response += data
            
        # Display the raw response in the terminal
        print(response.decode('utf-8'))
        
    except ConnectionRefusedError:
        print(f"[-] Connection refused. Ensure the Proxy Server is running on port {PROXY_PORT}.")
    except Exception as e:
        print(f"[-] An error occurred: {e}")
    finally:
        client_socket.close()
        print("\n[*] TCP connection closed.")

def run_udp_mode():
    """
    Phase 2: UDP Mode (QoS Tester)
    Sends 10 ping packets to the Web Server and calculates QoS metrics.
    """
    print(f"[*] Starting UDP Mode. Pinging Web Server ({WEBSERVER_IP}:{WEBSERVER_PORT})...\n")
    
    # Initialize UDP socket (SOCK_DGRAM)
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Requirement: 1-second timeout per packet
    udp_socket.settimeout(1.0)
    
    # TODO: Implement the 10-packet loop here
    # 1. Generate timestamp (time.time())
    # 2. Format payload: f"Ping {seq} {timestamp}"
    # 3. udp_socket.sendto(...)
    # 4. Measure RTT on successful recvfrom(), handle socket.timeout exception
    # 5. Calculate and print Min/Avg/Max RTT, Jitter, and Packet Loss
    
    print("[!] UDP QoS logic needs to be implemented.")
    udp_socket.close()

if __name__ == '__main__':
    # Set up command line arguments
    parser = argparse.ArgumentParser(description="Client module for Client-Proxy-Server architecture.")
    parser.add_argument('-mode', choices=['tcp', 'udp'], required=True, help="Operating mode: 'tcp' for HTTP or 'udp' for QoS Ping")
    parser.add_argument('-file', default='/index.html', help="File to request in TCP mode (default: /index.html)")
    
    args = parser.parse_args()

    if args.mode == 'tcp':
        run_tcp_mode(args.file)
    elif args.mode == 'udp':
        run_udp_mode()