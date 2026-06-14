# Computer-Networks-Final-Project

Implementation and Performance Analysis of a Python Socket-Based Client–Proxy–Server System

This project implements a Client–Proxy–Server architecture using low-level Python socket programming as part of the Computer Networks final project. The system supports HTTP communication through a Proxy Server, file-based caching, UDP Echo services for QoS evaluation, and multithreaded request handling. In addition to demonstrating core networking concepts, the project also explores performance analysis through Wireshark-based traffic inspection and Quality of Service measurements.

Features

* HTTP communication using TCP sockets
* Proxy forwarding and file-based caching
* Cache HIT and Cache MISS mechanisms
* UDP Echo service for QoS evaluation
* Multithreaded request handling
* Browser-based website access
* Custom HTTP error pages (404, 500, 502, and 504)
* Wireshark packet analysis and traffic verification

Results

The caching mechanism significantly improved system performance by reducing response time by approximately 98%, from 3435.82 ms during Cache MISS to 70.44 ms during Cache HIT. The system successfully handled five concurrent clients without connection failures and maintained 0% packet loss across all QoS testing scenarios. Further analysis also highlighted the effects of sequential I/O operations and concurrent processing on RTT and jitter behaviour.

Deliverables

This repository also includes supporting deliverables used throughout development and evaluation, including Wireshark captures, demonstration scripts, troubleshooting records, and project progress documentation. These materials provide additional evidence of the testing methodology, engineering decisions, and performance analyses presented in the final report.

Limitations and Future Work

The current implementation does not include cache expiration mechanisms or TLS/SSL encryption, limiting its use to controlled environments. Future enhancements may include implementing LRU and TTL-based cache management, integrating secure communication protocols, and adopting a fixed-size thread pool architecture to improve scalability and robustness.

Authors

* Axella N. H
* Anita W. M

Computer Networks – Final Project
