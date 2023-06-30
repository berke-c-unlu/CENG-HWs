from socket import *
from threading import *
from components import *
import argparse
import Graph
import User
import random
import uuid
import hashlib
import PIL
import time
import sys
import json
import sqlite3

parser = argparse.ArgumentParser()
parser.add_argument('--port', dest='port', type=int, help='Port number')
args = parser.parse_args()

port = args.port

graphs = []
session = {}
session_lock = Lock()
graphs_lock = Lock()

# open sqlite3 database
conn = sqlite3.connect('graph-image-tool.db', check_same_thread=False)


#u1 = User.User("bugra","bugra@abc.com","Buğra Burak Altıntaş","bugra123")
#u2 = User.User("berke","berke@abc.com","Berke Can Ünlü","berke3138")


db = [
    {
        "username" : "bugra",
        "email" : "bugra@abc.com",
        "fullname" : "Bugra Burak Altintas",
        "password" : hashlib.sha256("bugra123".encode('utf-8')).hexdigest()
    },
    {
        "username" : "berke",
        "email" : "berke@abc.com",
        "fullname" : "Berke Can Unlu",
        "password" : hashlib.sha256("berke123".encode('utf-8')).hexdigest()
    },
    {
        "username" : "can",
        "email" : "can@abc.com",
        "fullname" : "Can Unlu",
        "password" : hashlib.sha256("can123".encode('utf-8')).hexdigest()
    },
    {
        "username" : "burak",
        "email" : "burak@abc.com",
        "fullname" : "Burak Altintas",
        "password" : hashlib.sha256("can123".encode('utf-8')).hexdigest()
    }
]

def __callback_function(message):
    print(message)

def get_node_class(node_class):
    if node_class == "load_image":
        return LoadImage.LoadImage
    elif node_class == "save_image":
        return SaveImage.SaveImage
    elif node_class == "crop":
        return Crop.Crop
    elif node_class == "dup_image":
        return DupImage.DupImage
    elif node_class == "fit":
        return Fit.Fit
    elif node_class == "get_dimensions":
        return GetDimensions.GetDimensions
    elif node_class == "get_float":
        return GetFloat.GetFloat
    elif node_class == "get_integer":
        return GetInteger.GetInteger
    elif node_class == "h_stack":
        return HStack.HStack
    elif node_class == "rotate":
        return Rotate.Rotate
    elif node_class == "scale":
        return Scale.Scale
    elif node_class == "stack":
        return Stack.Stack
    elif node_class == "stretch":
        return Stretch.Stretch
    elif node_class == "view_image":
        return ViewImage.ViewImage




def get_graph(graph_name):
    global graphs

    for graph in graphs:
        if graph.name == graph_name:
            return graph
    
    return None


def agent(sock):
    global graphs

    sock.send("Welcome to the server!".encode())
    req = sock.recv(65536)
    while req and req != b'':
        s = req.decode().strip().split(" ")
        reply = ""
        try:
            if s[0] == 'register':
                username = s[1]
                password = s[2]
                email = s[3]
                fullname = " ".join(s[4:])
                print("register",username,password,email,fullname)

                # check if username in sqlite3 database
                c = conn.cursor()
                c.execute("SELECT * FROM users WHERE username = ?",(username,))
                if c.fetchone() != None:
                    raise Exception("username already exists in db")
                
                usernames = []
                for user in session.values():
                    usernames.append(user.username)

                if username in usernames:
                    raise Exception("you are already logged in")

                # add user to sqlite3 database
                hash_pass = hashlib.sha256(password.encode()).hexdigest()
                c = conn.cursor()
                c.execute("INSERT INTO users ('username','password','email','fullname') VALUES(?,?,?,?)",(username,hash_pass,email,fullname))
                conn.commit()

                # reply
                reply += "registered " + username

            # handle login
            # msg : login username password
            elif s[0] == "login":
                username = s[1]
                password = s[2]
                print("login",username,password)

                usernames = []
                for user in session.values():
                    usernames.append(user.username)

                if username in usernames:
                    raise Exception("you are already logged in")
                
                # check if user exists in sqlite3 database
                c = conn.cursor()
                c.execute("SELECT username FROM users WHERE username = ?",(username,))
                if c.fetchone() == None:
                    raise Exception("user not found in db")
                
                else:
                    # if user exists in sqlite3 database
                    # get password from sqlite3 database
                    c = conn.cursor()
                    c.execute("SELECT * FROM users WHERE username = ?",(username,))
                    _id,db_username,db_password,db_email,db_fullname = c.fetchone()
                    curr_user = User.User(db_username,db_email,db_fullname,db_password)

                    # check if password is correct
                    if curr_user.auth(password):
                        # create token
                        token = curr_user.login()
                        # add token to session
                        with session_lock:
                            session[token] = curr_user

                        # send token to client
                        reply += "token " + str(token)
                    else:
                        raise Exception("wrong password")
                
            # handle logout
            # msg : logout token
            elif s[0] == "logout":
                # get token
                token = uuid.UUID(s[1])

                if token not in session:
                    raise Exception("you need to login first to logout")

                # logout user
                session[token].logout()
                # delete token from session
                with session_lock:
                    del session[token]
                reply += "logout successful"
            
            # handle create graph
            # msg : new graph_name token
            elif s[0] == "new":
                graph_name = s[1]
                token = uuid.UUID(s[2])

                if token not in session:
                    raise Exception("You need to login first to create a graph")
                
                if graph_name in [graph.name for graph in graphs]:
                    raise Exception("Graph {} is already added".format(graph_name))
                

                g = Graph.Graph(graph_name,session[token])
                # create graph
                with graphs_lock:
                    # add graph to graphs
                    graphs.append(g)

                reply += "new graph created"

            # handle list graphs
            # msg : list token
            elif s[0] == "list":
                token = uuid.UUID(s[1]) if s[1] != "not_logged_in" else None
                # list graphs
                graph_list = []
                with graphs_lock:
                    for graph in graphs:
                        graph_list.append(json.loads(str(graph)))
                data = {"graphs" : graph_list,"opened" : "None"}
                if token != None:
                    if token not in session:
                        raise Exception("you need to login first to list graphs")
                    else:
                        data["opened"] = session[token].get_curr_graph().name if session[token].get_curr_graph() != None else "None"
                reply += json.dumps(data)
                if reply == '':
                    raise Exception("no graphs found")


            # handle open graph
            # msg : open graph_name mode token
            elif s[0] == "open":
                # get graph name, mode and token
                graph_name = s[1]
                mode = s[2]
                token = uuid.UUID(s[3])

                user : User.User = session[token]

                if token not in session:
                    raise Exception("You need to login first to open a graph")
                
                if user.get_curr_graph() != None:
                    raise Exception("The graph {} is already open, you need to close it first".format(user.get_curr_graph().name))

                with graphs_lock:
                    user.set_curr_graph(get_graph(graph_name))

                if user.get_curr_graph() == None:
                    raise Exception("Graph {} not found".format(graph_name))
                
                # set callback function
                callback = __callback_function

                # attach user to graph
                # while other threads are waiting, send message to client
                with user.get_curr_graph().monitor.mutex:
                    while user.get_curr_graph().inprogress:
                        user.get_curr_graph().monitor.wait()

                    user.get_curr_graph().inprogress = True
                    user.get_curr_graph().attach(session[token], mode, callback)
                    user.get_curr_graph().inprogress = False
                    user.get_curr_graph().monitor.notify_all()

                reply += "graph opened"


            # handle close graph
            # msg : close token
            elif s[0] == "close":
                token = uuid.UUID(s[1])

                user : User.User = session[token]

                if token not in session:
                    raise Exception("You need to login first to close a graph")
                
                if user.get_curr_graph() == None:
                    raise Exception("Graph is not opened")
                
                # set callback function
                callback = __callback_function

                with user.get_curr_graph().monitor.mutex:
                    while user.get_curr_graph().inprogress:
                        user.get_curr_graph().monitor.wait()

                    user.get_curr_graph().inprogress = True
                    user.get_curr_graph().detach(user,callback)
                    user.get_curr_graph().inprogress = False

                    user.get_curr_graph().monitor.notify_all()

                with graphs_lock:
                    user.set_curr_graph(None)

                reply += "close graph"



            # handle add node
            # msg : add node_class token
            elif s[0] == "add":
                node_class = get_node_class(s[1])
                token = uuid.UUID(s[2])

                user : User.User = session[token]

                if token not in session:
                    raise Exception("you need to login first to add a node")
                
                if user.get_curr_graph() == None:
                    raise Exception("Graph has not been opened before.")
                
                # add node to graph
                with user.get_curr_graph().monitor.mutex:
                    while user.get_curr_graph().inprogress:
                        user.get_curr_graph().monitor.wait()

                    user.get_curr_graph().inprogress = True
                    user.get_curr_graph().newnode(node_class)
                    user.get_curr_graph().inprogress = False

                    user.get_curr_graph().monitor.notify_all()
                reply += "node added"


            # handle connect nodes
            # msg : connect node1 outport node2 inport token
            elif s[0] == "connect":
                node1 = int(s[1])
                outport = s[2]
                node2 = int(s[3])
                inport = s[4]
                token = uuid.UUID(s[5])

                user : User.User = session[token]

                if token not in session:
                    raise Exception("you need to login first to connect nodes")
                
                if user.get_curr_graph() == None:
                    raise Exception("Graph has not been opened before.")

                if len(user.get_curr_graph().graph) <= node1 or len(user.get_curr_graph().graph) <= node2:
                    raise Exception("There is no node with that id")
                
                if 'outports' in dir(user.get_curr_graph().graph[node1].component) and outport not in user.get_curr_graph().graph[node1].component.outports:
                    raise Exception("There is no outport with that name in node{}".format(node1))

                if 'inports' not in dir(user.get_curr_graph().graph[node2].component) and inport not in user.get_curr_graph().graph[node2].component.inports:
                    raise Exception("There is no inport with that name in node{}".format(node2))
            
                # get nodes from graphs keys
                with user.get_curr_graph().monitor.mutex:
                    while user.get_curr_graph().inprogress:
                        user.get_curr_graph().monitor.wait()

                    user.get_curr_graph().inprogress = True
                    node1 = user.get_curr_graph().graph[node1]
                    node2 = user.get_curr_graph().graph[node2]
                    user.get_curr_graph().connect(node1,outport,node2,inport)
                    user.get_curr_graph().inprogress = False

                    user.get_curr_graph().monitor.notify_all()
                reply += "nodes connected"

            # handle disconnect nodes
            # msg : disconnect node1 outport node2 inport token
            elif s[0] == "disconnect":
                node1 = int(s[1])
                outport = s[2]
                node2 = int(s[3])
                inport = s[4]
                token = uuid.UUID(s[5])

                user : User.User = session[token]

                if token not in session:
                    raise Exception("you need to login first to connect nodes")
                
                if user.get_curr_graph() == None:
                    raise Exception("Graph has not been opened before.")

                if len(user.get_curr_graph().graph) <= node1 or len(user.get_curr_graph().graph) <= node2:
                    raise Exception("There is no node with that id")

                if 'outports' in dir(user.get_curr_graph().graph[node1].component) and outport not in user.get_curr_graph().graph[node1].component.outports:
                    raise Exception("There is no outport with that name in node{}".format(node1))

                if 'inports' not in dir(user.get_curr_graph().graph[node2].component) and inport not in user.get_curr_graph().graph[node2].component.inports:
                    raise Exception("There is no inport with that name in node{}".format(node2))

                with user.get_curr_graph().monitor.mutex:
                    while user.get_curr_graph().inprogress:
                        user.get_curr_graph().monitor.wait()

                    user.get_curr_graph().inprogress = True
                    node1 = user.get_curr_graph().graph[node1]
                    node2 = user.get_curr_graph().graph[node2]
                    user.get_curr_graph().disconnect(node1,outport,node2,inport)
                    user.get_curr_graph().inprogress = False

                    user.get_curr_graph().monitor.notify_all()
                reply += "nodes disconnected"


            # handle getcomponenttypes
            # msg : getcomponenttypes token
            elif s[0] == "getcomponenttypes":
                token = uuid.UUID(s[1])

                user : User.User = session[token]

                if token not in session:
                    raise Exception("you need to login first to get component type")
                
                if user.get_curr_graph() == None:
                    raise Exception("Graph has not been opened before.")

                # get component type
                with user.get_curr_graph().monitor.mutex:
                    while user.get_curr_graph().inprogress:
                        user.get_curr_graph().monitor.wait()

                    user.get_curr_graph().inprogress = True
                    reply += user.get_curr_graph().getcomponenttypes()
                    user.get_curr_graph().inprogress = False

                    user.get_curr_graph().monitor.notify_all()


            # handle execute graph
            # msg : execute token
            elif s[0] == "execute":
                token = uuid.UUID(s[1])

                user : User.User = session[token]

                if token not in session:
                    raise Exception("You need to login first to execute a graph")
                
                if user.get_curr_graph() == None:
                    raise Exception("Graph has not been opened before.")


                with user.get_curr_graph().monitor.mutex:
                    while user.get_curr_graph().inprogress:
                        user.get_curr_graph().monitor.wait()

                    user.get_curr_graph().inprogress = True
                    sock.send("runparams".encode())
                    size = sock.recv(65536).decode()
                    print("size:", size)
                    sock.send(b'size_received')
                    data = b''
                    while len(data) < int(size):
                        data += sock.recv(1024)
                    params = json.loads(data.decode())

                    user.get_curr_graph().execute(params)
                    user.get_curr_graph().inprogress = False

                    user.get_curr_graph().monitor.notify_all()

                reply += "Graph executed"

            elif s[0] == "outports":
                nodeid = int(s[1])
                token = uuid.UUID(s[2])

                user : User.User = session[token]

                if token not in session:
                    raise Exception("you need to login first to get outports")
                
                if user.get_curr_graph() == None:
                    raise Exception("Graph has not been opened before.")

                with user.get_curr_graph().monitor.mutex:
                    while user.get_curr_graph().inprogress:
                        user.get_curr_graph().monitor.wait()

                    user.get_curr_graph().inprogress = True
                    if nodeid > len(user.get_curr_graph().graph)-1:
                        user.get_curr_graph().inprogress = False
                        user.get_curr_graph().monitor.notify_all()
                        raise Exception("There is no node with that id")
                    reply += str(user.get_curr_graph().graph[nodeid]);
                    user.get_curr_graph().inprogress = False

                    user.get_curr_graph().monitor.notify_all()

            elif s[0] == "exit":
                break  
            else:
                raise Exception("invalid command" + str(s))
        except Exception as e:
            print(e)
            reply += "something went wrong: " + str(e)
        sock.send(reply.encode())
        req = sock.recv(65536)
    print(sock.getpeername(), ' closing connection')
    sock.close()

def server(port):
    s = socket(AF_INET, SOCK_STREAM)
    s.bind(('',port))
    s.listen()
    print("server started")
    try:
        while True:
            ns, peer = s.accept()
            print(peer, "connected")
            # create a thread with new socket
            t = Thread(target = agent, args=(ns,))
            t.start()
            # now main thread ready to accept next connection
    finally:
        s.close()

server = Thread(target=server, args=(port,))
server.start()
