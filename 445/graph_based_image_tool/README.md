# **A Graph Based Image Editing and Processing Tool**

Group members:
- Berke Can Ünlü - 2381028
- Buğra Burak Altıntaş - 2380079

## Description

In this project, we are providing a graph based image editing and processing tool which a user can create a pipeline consisting some image editing and processing operations such as cropping, rotating, duplicating an image. A user creates a graph and adds nodes by selecting an operation for each node. Then, user connects these nodes to construct a pipeline with selected operations. We provide 14 different operations in separate classes in **components** folder with their names. There is a base class **Component** for all components we have in component.py. Purpose of this class is to create an interface for the components we have to implement certain functions. Also, the **Component** class is derived from **multiprocessing.Process** class since each component will run in separate processes when the graph is executed. We override the **run** function of Process class so that the component reads inputs from its inports and executes with these inputs, then returns the outputs to outports. In **execute** function, the operation corresponding to component is executed on given inputs and output is returned. 

There is a **Graph** class in graph.py to connect the added nodes to construct a pipeline and execute the operations on given input image. In Graph class, we have a **Node** class implementation to store a component and a unique id assosicated with it. After the user creates new nodes with **Graph.newnode** function, user connects them by calling **connect** function and providing outport name of first node and inport name of the second node as parameters. When the connect function is called, we create a **multiprocessing.Pipe** and assign the returned **connection** objects to indicated ports. When the graph is executed, components receive inputs from and send output to these pipes. In **disconnect** function, we simply assign the indicated inports to None. TO provide parameters to interactive components, such as LoadImage and GetInteger, **runparams** function is called. This function traverses the graph and ask for input for each interactive component, then store these inputs with each node's id. When graph is executed with **execute** function, collected parameters is given to interactive components and each component is started as separate processes.


# Input / Output

Example input file is inputs/lena.png.
To get an output please give the output as outputs/*.png

# TCP/IP Client-Server Application

A client-server application is implemented which supports multiple clients connection to server. When server is started, it starts to listen at the port given as argument. Whenever a client requests to connect to the server, it accepts the request and creates a separate socket to serve this client.Then, the server starts an **agent** thread for the client. Each agent is responsible for one client. So, multiple clients are served concurrently.<br> 
The application works with the commands sent from clients. Provided commands are listed below:
* login username password
* logout
* new graph_name
* open graph_name mode
* close
* list
* add component_type
* connect node1_id outport node2_id inport
* disconnect node1_id outport node2_id inport
* getcomponenttypes
* execute <br>
When a client sends a command, it is parsed at the server agent and required action is taken.

## Authentication
When a client sends a login command with credentials, they are checked whether they exists in the memory. If they exist and are correct, agent calls ’login()’ function of user returning a token. The user is recorded to a ’session’ dictionary where the token is the key and user object is the value. Then, the token is sent to the client to use it for sending other messages. For each operation, the client appends this token to the command. In server side, the token is checked whether it is still valid. <br>
When a client sends a ’logout’ command, corresponding user is removed from ’session’ and its token is invalidated.

## Operations
All operations on the graph are working in critical region. The exclusive access is provided with a monitor object. Each graph has its own monitor object and all accesses are controlled with this monitor object.
* Only operation that does not require authentication is ’list’. It lists all graphs and users attached to it. <br>
* ’new graph_name’ command creates an empty graph named with the given parameter ’graph_name’.
* ’open graph_name mode’ command open the graph with given parameter ’graph_name’ with the given ’mode’. At this time ’mode’ is not functional. All users can edit and read the graph. Following commands after this command will be applied on the current graph instance.
* ’close’ command closes the current graph instance. 
* ’add component_type’ adds a new node to the current graph instance with given component type.
* ’connect node1_id outport node2_id inport’ connects dedicated outport of node1 to dedicated inport of node2. IDs of nodes are given as parameters.
* ’disconnect node1_id outport node2_id inport’ disconnects dedicated outport of node1 from dedicated inport of node2. IDs of nodes are given as parameters.
* ’getcomponenttypes’ command lists the types of components in current graph instance.
* ’execute’ command executes the graph. For interactive components, it asks for inputs from client. For LoadImage component, the client enters a local path of an image. The image at the given path is loaded at client side and sent to server over TCP connection. For other interactive components, the client enters the requested value. Then, the graph is executed with given parameters. The validity of graph is checked before execution.


# How to run client-server application
```bash
python3 server.py --port <port_number>
python3 client.py --port <port_number>
```
