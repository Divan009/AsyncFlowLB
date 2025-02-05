# Load Balancer Design Document

## Table of Contents
1. [Introduction](#introduction)
2. [Architecture Overview](#architecture-overview)
3. [Components](#components)
   - [1. LoadBalancer](#1-loadbalancer)
   - [2. HealthCheck](#2-healthcheck)
   - [3. ServerPool](#3-serverpool)
   - [4. Load Balancing Algorithms](#4-load-balancing-algorithms)
4. [Design Patterns Utilized](#design-patterns-utilized)
   - [Strategy Pattern](#strategy-pattern)
   - [Factory Pattern](#factory-pattern)
5. [Interaction Flow](#interaction-flow)
   - [1. Initialization](#1-initialization)
   - [2. Health Checking](#2-health-checking)
   - [3. Request Handling](#3-request-handling)
     - [a. HTTP Requests](#a-http-requests)
     - [b. TCP Connections](#b-tcp-connections)
   - [4. Load Balancing](#4-load-balancing)
6. [Error Handling](#error-handling)
7. [Concurrency Considerations](#concurrency-considerations)
8. [Testing Strategy](#testing-strategy)
9. [Future Enhancements](#future-enhancements)
10. [Conclusion](#conclusion)

---

## Introduction
This document outlines the design and architecture of a custom Load Balancer developed in Python. The Load Balancer is designed to distribute incoming HTTP and TCP requests across a pool of backend servers, ensuring high availability, scalability, and reliability. It incorporates health checks to monitor server statuses and utilizes the **Strategy Pattern** to support multiple load balancing algorithms, such as Round Robin, Weighted Round Robin, and Least Connections.

---

## Architecture Overview
The Load Balancer is structured into modular components, each responsible for specific functionalities:

- **LoadBalancer**: Core component that initializes and manages the load balancing process.
- **HealthCheck**: Monitors the health of backend servers, marking them as healthy or unhealthy.
- **ServerPool**: Maintains the list of backend servers and their statuses.
- **Load Balancing Algorithms**: Implements different strategies to select the most suitable server for handling requests.

The system leverages asynchronous programming (via `asyncio` and `aiohttp`) to handle multiple concurrent connections efficiently.

---

## Components

### 1. LoadBalancer
**Purpose**: Acts as the central orchestrator, initializing servers, handling incoming requests, and coordinating with other components like `HealthCheck` and `ServerPool`.

**Key Responsibilities**:
- **Initialization**: Sets up HTTP and TCP servers based on configuration.
- **Request Handling**: Receives incoming requests and forwards them to healthy backend servers using the selected load balancing algorithm.
- **Shutdown**: Gracefully shuts down servers and cleans up resources.

**Core Methods**:
- `start()`: Initiates health checks and starts the appropriate server (HTTP/TCP).
- `start_http_server()`: Sets up and runs the HTTP server using `aiohttp`.
- `start_tcp_server()`: Sets up and runs the TCP server using `asyncio`.
- `shutdown()`: Handles graceful shutdown procedures.

---

### 2. HealthCheck
**Purpose**: Continuously monitors the health of backend servers, ensuring that only healthy servers receive traffic.

**Key Responsibilities**:
- **Health Monitoring**: Periodically checks the status of each server using specified protocols (HTTP/TCP).
- **State Management**: Marks servers as healthy or unhealthy based on health check results.
- **Integration**: Notifies the `LoadBalancer` to update the algorithm when server health statuses change.

**Core Methods**:
- `start()`: Initializes resources and begins the health checking loop.
- `run()`: Continuously performs health checks at defined intervals.
- `check_server()`: Executes the health check logic for a single server.
- `mark_healthy()`: Marks a server as healthy and updates the server pool.
- `mark_unhealthy()`: Marks a server as unhealthy and updates the server pool.
- `close()`: Cleans up resources and stops health checking.

---

### 3. ServerPool
**Purpose**: Maintains the pool of backend servers, tracking their availability and statuses.

**Key Responsibilities**:
- **Server Management**: Stores and updates the list of backend servers.
- **Status Tracking**: Keeps track of each server's health status (healthy/unhealthy).
- **Thread Safety**: Ensures safe concurrent access to server data.

**Core Methods**:
- `get_all_servers()`: Retrieves the complete list of servers.
- `get_healthy_servers()`: Retrieves only the healthy servers.
- `mark_unhealthy(server)`: Marks a specific server as unhealthy.
- `mark_healthy(server)`: Marks a specific server as healthy.

---

### 4. Load Balancing Algorithms
**Purpose**: Implements various strategies to select the most appropriate backend server for handling incoming requests.

**Key Responsibilities**:
- **Server Selection**: Determines which server should handle a given request based on the algorithm.
- **Extensibility**: Supports adding new algorithms without modifying existing code.

**Implemented Algorithms**:
- **RoundRobinAlg**: Distributes requests evenly in a circular order.
- **WeightedRoundRobinAlg**: Distributes requests based on assigned server weights.
- **LeastConnectionsAlg**: Selects the server with the fewest active connections.

**Core Interfaces**:
- `BaseAlgorithm`: Abstract base class defining the `select_server` method.
- Concrete Algorithms (`RoundRobinAlg`, `WeightedRoundRobinAlg`, `LeastConnectionsAlg`): Implement the `BaseAlgorithm`.

---

## Design Patterns Utilized

### Strategy Pattern
- **Definition**: Defines a family of algorithms, encapsulates each one, and makes them interchangeable.
- **Application**:
  - **Context**: `AlgorithmContext` holds a reference to a `BaseAlgorithm`.
  - **Strategy**: Concrete algorithms (e.g., `RoundRobinAlg`) implement the selection logic.
  - **Factory**: `AlgorithmFactory` creates instances of strategies based on configuration.
- **Benefits**:
  - Flexibility and extensibility.
  - Promotes separation of concerns.

---

### Factory Pattern
- **Definition**: Provides an interface for creating objects but allows subclasses to determine the object type.
- **Application**: 
  - `AlgorithmFactory` creates instances of load balancing algorithms based on configuration.
- **Benefits**:
  - Decouples object creation from usage.
  - Facilitates adding new algorithms without altering client code.

---

## Interaction Flow

### 1. Initialization
- **Configuration Loading**: `LoadBalancer` is initialized with a `LoadBalancerConfig` containing settings.
- **Component Setup**:
  - `ServerPool` is initialized with backend servers.
  - `HealthCheck` monitors server health and integrates with the `LoadBalancer`.
  - Load balancing algorithm is selected using `AlgorithmFactory`.

---

### 2. Health Checking
- `HealthCheck` periodically checks each server.
- Healthy and unhealthy statuses are updated in `ServerPool`.

---

### 3. Request Handling

#### a. HTTP Requests
- **Steps**:
  1. Retrieve healthy servers.
  2. Select a server using the algorithm.
  3. Forward the request using `aiohttp`.

#### b. TCP Connections
- **Steps**:
  1. Retrieve healthy servers.
  2. Select a server.
  3. Relay data between the client and the selected server.

---

### 4. Load Balancing
- Executes the selected algorithm to pick the most suitable server from the healthy pool.

---

## Error Handling
- **No Healthy Servers**:
  - HTTP: Respond with 503.
  - TCP: Close the client connection.
- **Forwarding Failures**: Log the error and return 502.
- **Health Check Failures**: Retry with exponential backoff.

---

## Concurrency Considerations
- Use `asyncio.Lock` for asynchronous synchronization in shared resources like `ServerPool` and load balancing algorithms.

---

## Testing Strategy
1. **Unit Tests**:
   - Component-level tests for `LoadBalancer`, `HealthCheck`, `ServerPool`, and algorithms.
2. **Integration Tests**:
   - Verify the interaction between components.
3. **Mocking**:
   - Use mock servers and health checks for controlled tests.

---

## Future Enhancements
- Add support for custom health check protocols.
- Implement connection draining for smoother server shutdowns.
- Add observability features like metrics and tracing.

---

## Conclusion
The modular design of the Load Balancer ensures scalability, flexibility, and maintainability. By leveraging modern patterns and practices, it can handle dynamic workloads efficiently.
