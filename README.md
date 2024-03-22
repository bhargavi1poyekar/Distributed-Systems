# Car Hire Distributed System

## Abstract:

Customers and Managers, need to handle transactions related to car from any place 
at a moment’s notice. These transactions may include, checking availability of cars, 
booking a car, adding/ removing a car, etc. A distributed database system separates a 
business's data by business function or geographical area. Car booking systems often use 
distributed systems, because these systems are configured to carry out specific business 
tasks in different locations while allowing those locations to communicate freely with one 
another. These systems offer car hiring systems several advantages over non-distributed 
systems. 

## System Diagram:

![](https://i.postimg.cc/7hyfKHqJ/image.png)

The client sends a request for performing any transaction to the load balancer. The load 
balancer sends the request to the appropriate server depending upon the load on each server. 
Also, all the servers periodically send their server time to the clock server which 
synchronizes the time and sends the synchronized time to all the servers.

## Components: 
1. Customers 
    *   Customers access the system for various transactions such as checking 
availability of the car, booking, paying and rating. 
    * The client will get a menu on the screen to select the transaction of their choice. 

2. Servers 
    * Servers perform the transactions which are requested by the client. 
    * Servers use the mutual exclusion principle while performing the above 
operations to maintain consistency. 

3. Clock Server 
    * The clock server synchronizes all the servers in the system using Berkely’s Algorithm. 
    * It takes the system time from the servers and sends back the synchronized time to all the servers in the system. 

4. Election Server 
    * The election server implements the Ring Election algorithm to determine the coordinator server among all the servers. 
    * It ensures that when an election starts it concludes with all the servers agreeing on who the coordinator should be. 

5. Load Balancer 
    * The load balancer implements the Round Robin Algorithm. 
    * It distributes a set of tasks over a set of servers to make their overall processing more efficient. 
    * It optimizes the response time and avoids unevenly overloading some compute nodes while other compute nodes are left idle.

6. Database Servers 
    * Multiple database servers improve the availability of data. 
    * It maintains copies of its data on multiple servers in order to provide high availability and scalability. 
    * When an application makes a change to a data item on one server, that change has to be propagated to the other replicas. 
    * Data consistency and replication is achieved by using a Data Centric Model and the Replicated Write Protocol. 

## Implementation: 

1. Client Server based program using RPC/RMI:

The client sends a request for performing any transaction to the load balancer. The 
load balancer sends the request to the appropriate server depending upon the load on 
each server. Also, all the servers periodically send their server time to the clock 
server which synchronizes the time and sends the synchronized time to all the 
servers. 

2. Implementation of Clock Synchronization :

It is possible that clocks of different servers become unmatched over time. 
Therefore, clock synchronization using Berkeley’s Algorithm is implemented so that 
all the servers have the same synchronized time. All the servers periodically send 
their times to the clock server. The clock server is a centralized server which 
continuously listens to the incoming connections and sends the synchronized time 
as the average of time differences of all the servers. 

3. Implementation of Election algorithm:

In distributed systems, there is a need for the node which can act as a coordinator to 
manage all the nodes in the system. Hence, the Election Algorithm is implemented 
to elect the coordinator server which can also assist in the tasks of clock 
synchronization, load balancing, etc. We implemented a Ring Election Algorithm 
that forms a logical ring among all the servers and hence can send the check 
messages in ring fashion. 

4. Implementation of Mutual Exclusion algorithm:

In distributed systems, it is possible that multiple processes access the same shared 
resource. This can lead to race conditions and hence a concurrency protocol is 
needed to ensure that all the processes are synchronised. We implemented a 
Centralised Mutual Exclusion Algorithm in which a central coordinator is elected 
and grants permission to enter the critical section and keeps a queue of requests to 
enter the critical section. 

5. Implement Load Balancing:
If multiple clients are accessing the application at the same time, then there is a 
possibility that a single server gets overloaded with the requests. Hence the Round 
Robin Load Balancing algorithm is implemented so that all the requests are 
distributed equally among all the servers and no single server gets overwhelmed. 

6. Client Server based program to check data consistency. 

The application would fail to serve the client’s request if it has only one data store 
and it becomes unavailable. Hence replication is implemented in order to ensure that 
the system will be available all the time. It is necessary to make sure that all the data 
stores have consistent data. So, the data consistency is implemented using a Data 
Centric Model and applying a Replicated Write Protocol where all the data stores 
have consistent data all the time. 
