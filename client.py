import socket
import argparse
import time
import statistics
import threading

PROXY_IP = '127.0.0.1'
PROXY_PORT = 8080
WEBSERVER_IP = '127.0.0.1'
WEBSERVER_PORT = 9000
BUFFER_SIZE = 4096

def run_tcp_mode(filename):
    print(f"[*] TCP Client requesting '{filename}' via Proxy ({PROXY_IP}:{PROXY_PORT})...")
    
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        client_socket.connect((PROXY_IP, PROXY_PORT))
        request = f"GET {filename} HTTP/1.1\r\nHost: {PROXY_IP}:{PROXY_PORT}\r\nConnection: close\r\n\r\n"
        client_socket.sendall(request.encode('utf-8'))
        
        response = b""
        while True:
            data = client_socket.recv(BUFFER_SIZE)
            if not data:
                break
            response += data
            
        print(response.decode('utf-8'))
        
    except ConnectionRefusedError:
        print(f"[-] Connection refused. Ensure the Proxy Server is running on port {PROXY_PORT}.")
    except Exception as e:
        print(f"[-] An error occurred: {e}")
    finally:
        client_socket.close()

def run_udp_mode():
    print(f"[*] Starting UDP Mode. Pinging Web Server ({WEBSERVER_IP}:{WEBSERVER_PORT})...\n")
    
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.settimeout(1.0)
    
    num_packets = 10
    lost_packets = 0
    rtt_list = []
    
    for i in range(1, num_packets + 1):
        start_time = time.time()
        message = f"Ping {i} {start_time}"
        
        try:
            udp_socket.sendto(message.encode('utf-8'), (WEBSERVER_IP, WEBSERVER_PORT))
            
            data, _ = udp_socket.recvfrom(BUFFER_SIZE)
            end_time = time.time()
            
            rtt = (end_time - start_time) * 1000
            rtt_list.append(rtt)
            
            print(f"[+] Reply from {WEBSERVER_IP}: seq={i} time={rtt:.2f}ms")
            
        except socket.timeout:
            print(f"[-] Request timed out for seq={i}")
            lost_packets += 1
            
    udp_socket.close()
    
    print("\n--- QoS Ping Statistics ---")
    
    loss_percent = (lost_packets / num_packets) * 100
    print(f"Packets: Sent = {num_packets}, Received = {num_packets - lost_packets}, Lost = {lost_packets} ({loss_percent:.1f}% loss)")
    
    if rtt_list:
        min_rtt = min(rtt_list)
        max_rtt = max(rtt_list)
        avg_rtt = statistics.mean(rtt_list)
        
        jitter = 0.0
        if len(rtt_list) > 1:
            rtt_diffs = [abs(rtt_list[j] - rtt_list[j-1]) for j in range(1, len(rtt_list))]
            if len(rtt_diffs) > 1:
                jitter = statistics.stdev(rtt_diffs)
            else:
                jitter = rtt_diffs[0]
                
        print(f"RTT (ms): Min = {min_rtt:.2f}, Max = {max_rtt:.2f}, Avg = {avg_rtt:.2f}")
        print(f"Jitter (ms): {jitter:.2f}")
    else:
        print("No RTT data available (100% packet loss).")

def run_multi_mode(filename):
    print(f"[*] Starting Multi-Client Simulation (5 concurrent threads) requesting '{filename}'...\n")
    
    threads = []
    
    for i in range(5):
        t = threading.Thread(target=run_tcp_mode, args=(filename,))
        threads.append(t)
        t.start()
        
    for t in threads:
        t.join()
        
    print("\n[*] All 5 client instances completed successfully.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Client module for Client-Proxy-Server architecture.")
    parser.add_argument('-mode', choices=['tcp', 'udp', 'multi'], required=True, help="Operating mode: 'tcp', 'udp', or 'multi'")
    parser.add_argument('-file', default='/index.html', help="File to request in tcp/multi mode (default: /index.html)")
    
    args = parser.parse_args()

    if args.mode == 'tcp':
        run_tcp_mode(args.file)
    elif args.mode == 'udp':
        run_udp_mode()
    elif args.mode == 'multi':
        run_multi_mode(args.file)