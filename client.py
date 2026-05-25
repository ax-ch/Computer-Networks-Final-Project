import socket
import threading
import time
import statistics
import sys

# CONFIGURATION

SERVER_HOST = '127.0.0.1'
UDP_PORT = 9000

PROXY_HOST = '127.0.0.1'
PROXY_PORT = 8080

PACKET_COUNT = 10
TIMEOUT = 2

# READ MODE

mode = "normal"

if len(sys.argv) > 1:
    mode = sys.argv[1]

# TCP CLIENT FUNCTION

def tcp_client():

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    client_socket.connect((PROXY_HOST, PROXY_PORT))

    request  = "GET /page.html HTTP/1.1\r\n"
    request += f"Host: {PROXY_HOST}\r\n"
    request += "Connection: close\r\n\r\n"

    client_socket.sendall(request.encode())

    response = b""

    while True:
        chunk = client_socket.recv(4096)

        if not chunk:
            break

        response += chunk

    print("[CLIENT] Response received")

    client_socket.close()

# UDP QoS FUNCTION

def udp_qos_client():

    # Store RTT values
    rtt_list = []

    # Count lost packets
    lost_packets = 0

    # Create UDP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Set timeout
    client_socket.settimeout(TIMEOUT)

    print("=" * 50)
    print("UDP QoS Client Started")
    print("=" * 50)

    for i in range(PACKET_COUNT):

        message = f"PING {i+1}"

        try:
            # Record start time
            start_time = time.time()

            # Send packet
            client_socket.sendto(message.encode(), (SERVER_HOST, UDP_PORT))

            print(f"[SENT] {message}")

            # Receive echo response
            data, server_addr = client_socket.recvfrom(1024)

            # Record end time
            end_time = time.time()

            # Calculate RTT in milliseconds
            rtt = (end_time - start_time) * 1000

            rtt_list.append(rtt)

            print(f"[RECEIVED] {data.decode()}")

            print(f"RTT: {rtt:.2f} ms\n")

        except socket.timeout:

            print(f"[TIMEOUT] Packet {i+1} lost\n")

            lost_packets += 1

    # FINAL STATISTICS

    print("=" * 50)
    print("FINAL QoS STATISTICS")
    print("=" * 50)

    received_packets = PACKET_COUNT - lost_packets

    loss_percent = (lost_packets / PACKET_COUNT) * 100

    print(f"Packets Sent     : {PACKET_COUNT}")
    print(f"Packets Received : {received_packets}")
    print(f"Packets Lost     : {lost_packets}")
    print(f"Packet Loss      : {loss_percent:.2f}%")

    if rtt_list:

        print(f"\nMinimum RTT : {min(rtt_list):.2f} ms")

        print(f"Average RTT : {statistics.mean(rtt_list):.2f} ms")

        print(f"Maximum RTT : {max(rtt_list):.2f} ms")

    else:
        print("\nNo RTT data available")

    client_socket.close()

# MODE SELECTION

if mode == "normal":

    print("NORMAL TCP CLIENT MODE")

    tcp_client()

elif mode == "multi":

    print("=" * 50)
    print("MULTI CLIENT SIMULATION")
    print("=" * 50)

    threads = []

    for i in range(5):

        t = threading.Thread(target=tcp_client)

        threads.append(t)

        t.start()

    for t in threads:
        t.join()

    print("\nAll client instances completed.")

elif mode == "udp":

    udp_qos_client()

else:

    print("Invalid mode")
