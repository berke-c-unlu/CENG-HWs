from components import *
import User
from multiprocessing import Pipe
from threading import *
import socket
import base64
from PIL import Image
import json
import io
import copy



class Graph:
    """
    Graph class.
    It contains a dictionary of nodes.
    Each node contains a component object and an adjacency list.
    The adjacency list contains node ids.
    Key is the node id and value is a list of node ids.
    The graph is directed.

    """


    class Monitor:
        def __init__(self):
            self.mutex = RLock()
            self.cv = Condition(self.mutex)
        
        def wait(self):
            self.cv.wait()

        def notify(self):
            self.cv.notify()

        def notify_all(self):
            self.cv.notify_all()

    
    class Node:
        """
        Node class.
        Node contains a component object, an unique id.
        """
        # keep track of node ids

        def __init__(self,id, component : Component):
            """ Constructor for Node class.
            It initializes the component and the id.
            Id is unique.
            """
            self.component = component
            self.id = id

        def __str__(self) -> str:
            """ Returns a string representation of the node.

            Returns:
                str: String representation of the node.
            """

            data = {"id":str(self.id),"component":str(self.component),"inports":None,"outports":None}

            message = "Node id : " + str(self.id) + "\n" \
                + "\t" +"Component type : " + str(self.component) + "\n"
            
            # try to get inports and outports
            try:
                message += "\t\t" + "Component inports : " + str(self.component.inports) + "\n"
                data["inports"] = self.component.inports
            except:
                pass
            try:
                message += "\t\t" + "Component outports : " + str(self.component.outports) + "\n"
                data["outports"] = self.component.outports
            except:
                pass

            return json.dumps(data,indent=4)
        
    
    def __init__(self,name,owner : User.User):
        self.name = name
        self.owner = owner
        self.users = []
        self.graph = []
        self.count = 0
        self.monitor = self.Monitor()
        self.inprogress = False
        self.connections = []

    def __str__(self) -> str:
        """ Returns a string representation of the graph.
        
        Returns:
            str: String representation of the graph.
        """

        graph = {}
        graph["name"] = self.name
        graph["owner"] = self.owner.username
        graph["nodes"] = []

        for node in self.graph:
            graph["nodes"].append(json.loads(str(node)))

        
        return json.dumps(graph,indent=4)


    def get(self):
        """
        Returns the graph.
        """
        return self

    def delete(self):
        """
        Deletes the graph.
        """
        for node in self.graph:
            del node
    
    def attach(self,user : User.User,mode,callback):
        """
        Attach the user to the graph.
        """
        self.users.append(user)
        callback("User: " + user.get_username() + " attached to the graph: " + self.name)

    
    def detach(self,user : User.User,callback):
        """
        Detach the user from the graph.
        """
        self.users.remove(user)
        callback("User: " + user.get_username() + " detached from the graph: " + self.name)



    def newnode(self,componenttype):
        """ 
        Creates a new node with component type.
        It adds the node to the graph.
        Key is the component count and the component type as tuple.
        Value is the node object.

        Args:
            componenttype (Component): Direct class name of the component
        """
        # create a new component
        component = componenttype()

        # create a new node
        component_node = self.Node(self.count,component)
        self.count += 1
        # add the node to the graph
        self.graph.append(component_node)

        print("Node created with id : " + str(component_node.id))
        print("Component type : " + str(componenttype) + "\n")

    def connect(self,node1 : Node ,outport : str ,node2 : Node ,inport : str):
        """
        Connect the given port no of node 1 to import no of the node2 components

        Args:
            node1 (Node): Node 1
            outport (str): output port of node1
            node2 (Node): Node 2
            inport (str): input port of node2
        """
        self.connections.append((node1.id,outport,node2.id,inport))

        node1.component.outports[outport] = (node2.id,inport)
        node2.component.inports[inport] = (node1.id,outport)

        print("Connected : " + str(node1.id) + " : " + outport + " -> " + str(node2.id) + " : " + inport)


        
    def disconnect(self,node1 : Node ,outport : str ,node2 : Node ,inport : str):
        """ Disconnect the given port no of node 1 to import no of the node2 components

        Args:
            node1 (Node): Node 1
            outport (str): output port of node1
            node2 (Node): Node 2
            inport (str): input port of node2
        """
        self.connections.remove((node1.id,outport,node2.id,inport))

        # disconnect the ports
        node2.component.inports[inport] = None
        node1.component.outports[outport] = None

        print("Disconnected : " + str(node1.id) + " : " + outport + " -> " + str(node2.id) + " : " + inport)






    def isvalid(self) -> bool:
        """ Checks if the graph is ready to execute.

        Returns:
            bool: True if the graph is ready to execute, False otherwise.
        """
        # Check if there is a unconnected port in the graph
        for node in self.graph:
            try:
                # try to get inports and outports
                if None in node.component.inports.values() or None in node.component.outports.values():
                    print("Component " + str(type(node.component)) + " has unconnected ports")
                    return False
            except:
                pass
            

            

            # TYPECHECK

            return True


    def runparams(self,sock_info) -> dict:
        """ Get input parameters from the user for interactive components.

        Returns:
            dict: Dictionary of parameters. Key is the node id, value is the parameter.
        """
        params = {}
        for node in self.graph:
            if type(node.component) == LoadImage.LoadImage:
                sock_info.send(b'load_image_request ' + str(node.id).encode())
                size = sock_info.recv(1024)
                sock_info.send(b'size_received')

                data = b''
                while len(data) < int(size.decode()):
                    data += sock_info.recv(1024)

                img_dict = json.loads(data)
                img_data = base64.b64decode(img_dict['img'])

                img = Image.open(io.BytesIO(img_data))

                params[node.id] = img
            elif type(node.component) == SaveImage.SaveImage:
                sock_info.send(b'save_image_request ' + str(node.id).encode())
                path = sock_info.recv(4096)
                params[node.id] = path.decode()
            elif type(node.component) == GetInteger.GetInteger:
                sock_info.send(b'integer_request ' + str(node.id).encode())
                path = sock_info.recv(4096)
                params[node.id] = int(path.decode())
            elif type(node.component) == GetFloat.GetFloat:
                sock_info.send(b'float_request ' + str(node.id).encode())
                path = sock_info.recv(4096)
                params[node.id] = float(path.decode())

        
        return params

                

    def execute(self,params : dict):
        """ Execute the graph.

        Each component is started in a new process.
        They are connected with pipes.

        Args:
            params (dict): input parameters for interactive components.
        """
        print("Executing graph")
        # construct nodes again, should be unnecessary
        for node in self.graph:
            # create a new component
            comp = node.component.__class__()
            node.component = comp

        # set the parameters
        for node in self.graph:
            if str(node.id) in params.keys():
                if str(node.component) == "LoadImage component":
                    img_data = base64.b64decode(params[str(node.id)])
                    img = Image.open(io.BytesIO(img_data))

                    node.component.param = img

                else:
                    node.component.param = params[str(node.id)]
        
        for con in self.connections:
            inp,out = Pipe()
            # connect the pipe to the ports
            self.graph[con[0]].component.outports[con[1]] = inp
            self.graph[con[2]].component.inports[con[3]] = out
        
        if not self.isvalid():
            raise Exception("Graph is not valid")

        # start the components
        for node in self.graph:
            node.component.start()
        print("Processes running")

        # join the components
        for node in self.graph:
            node.component.join()
        print("Processes finished")
        
        for con in self.connections:
            # clear pipes
            self.graph[con[0]].component.outports[con[1]] = (con[2],con[3])
            self.graph[con[2]].component.inports[con[3]] = (con[0],con[1])



    def getcomponenttypes(self) -> set:
        """ Get the types of the components in the graph.

        Returns:
            set: Set of component types.
        """
        types = set()
        # for each node in the graph get the type of the component
        for node in self.graph:
            types.add(node.component)
        return types



    
        
    
