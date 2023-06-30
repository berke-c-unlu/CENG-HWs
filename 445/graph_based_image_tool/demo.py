############################################
# This is a demo file to show how to use the
# Graph class and the User class
############################################
############################################
# Student 1: Berke Can Ünlü - 2381028
# Student 2: Buğra Burak Altıntaş - 2380079
############################################


from components import *
import User
import Graph
from PIL import Image
import os


if __name__ == "__main__":
    # Create outputs folder if it doesn't exist
    if not os.path.exists("outputs"):
        os.makedirs("outputs")

    def __callback_function(message):
        print(message)

    # Create a user
    user = User.User("testuser","asd@asd.com", "12345678", "12345678")

    # print user
    print("User created:")
    print(user)
    print("--------------------")

    # Test getters and setters of user
    print("Testing getters and setters of user...")
    user.set_username("testusername")
    user.set_email("testemail@test.com")
    user.set_passwd("testpassword")
    user.set_fullname("test test")

    username = user.get_username()
    email = user.get_email()
    password = user.get_passwd()
    fullname = user.get_fullname()

    print("User after setters:")
    print("Username: " + username)
    print("Email: " + email)
    print("Password: " + password)
    print("Fullname: " + fullname)
    print("--------------------")

    # Create a graph
    print("Creating graph...")
    graph = Graph.Graph("testgraph",user)
    print("--------------------")

    # print graph
    print("Graph created:")
    print(graph)
    print("--------------------")

    # Attach user to graph
    print("Attaching user to graph...")
    print(user)
    graph.attach(user,None, __callback_function)
    print("--------------------")

    ##### Create nodes #####
    print("Creating nodes...")
    # Create LoadImage node
    graph.newnode(LoadImage.LoadImage)

    # Create Crop node
    graph.newnode(Crop.Crop)

    # Create GetInteger nodes
    for i in range(4):
        graph.newnode(GetInteger.GetInteger)

    # Create SaveImage node
    graph.newnode(SaveImage.SaveImage)

    # Create GetFloat node
    graph.newnode(GetFloat.GetFloat)

    # Create Rotate node
    graph.newnode(Rotate.Rotate)

    # Create DupImage node
    graph.newnode(DupImage.DupImage)

    # Create HStack node
    graph.newnode(HStack.HStack)

    # Create ViewImage node
    graph.newnode(ViewImage.ViewImage)

    # Create DupImage node
    graph.newnode(DupImage.DupImage)

    print("--------------------")

    # Get the graph
    get_graph = graph.get()

    # print get graph
    print("Graph:")
    print(get_graph)
    print("--------------------")

    # Connect nodes
    print("Connecting nodes...")
    keys,values = zip(*graph.graph.items())
    # LoadImage -> Crop
    graph.connect(keys[0], "output", keys[1], "input")
    # GetInteger -> Crop
    graph.connect(keys[2], "output", keys[1], "left")
    # GetInteger -> Crop
    graph.connect(keys[3], "output", keys[1], "top")
    # GetInteger -> Crop
    graph.connect(keys[4], "output", keys[1], "width")
    # GetInteger -> Crop
    graph.connect(keys[5], "output", keys[1], "height")
    # GetFloat -> Rotate
    graph.connect(keys[7], "output", keys[8], "angle")
    # Crop -> Rotate
    graph.connect(keys[1], "output", keys[8], "input")
    # Rotate -> DupImage
    graph.connect(keys[8], "output", keys[9], "input")
    # DupImage -> HStack
    graph.connect(keys[9], "output1", keys[10], "input1")
    # DupImage -> HStack
    graph.connect(keys[9], "output2", keys[10], "input2")
    # HStack -> DupImage
    graph.connect(keys[10], "output", keys[12], "input")
    # DupImage -> SaveImage
    graph.connect(keys[12], "output1", keys[6], "input")
    # DupImage -> ViewImage
    graph.connect(keys[12], "output2", keys[11], "input")
    print("--------------------")

    # print graph
    print("Graph:")
    print(graph.get())
    print("--------------------")

    # print component types
    print("Component types:")
    component_types = graph.getcomponenttypes()
    for component_type in component_types:
        print(component_type)
        print()
    print("--------------------")

    # print graph params
    print("Getting graph params...")
    params = graph.runparams()
    print("--------------------")

    # print params
    print("Params:")
    print(params)
    print("--------------------")

    # check if graph is valid
    print("Checking if graph is valid...")
    is_valid = graph.isvalid()
    if is_valid:
        print("Graph is valid")
    else:
        print("Graph is not valid, please check connections")
    print("--------------------")

    # Disconnect nodes
    print("Disconnecting nodes...")
    # Disconnect LoadImage -> Crop
    graph.disconnect(keys[0], "output", keys[1], "input")
    print("--------------------")

    # check if graph is valid
    print("Checking if graph is valid...")
    is_valid = graph.isvalid()
    if is_valid:
        print("Graph is valid")
    else:
        print("Graph is not valid, please check connections")
    print("--------------------")

    # Connect nodes
    # Connect LoadImage -> Crop
    print("Connecting nodes...")
    graph.connect(keys[0], "output", keys[1], "input")
    print("--------------------")

    # check if graph is valid
    print("Checking if graph is valid...")
    is_valid = graph.isvalid()
    if is_valid:
        print("Graph is valid")
    else:
        print("Graph is not valid, please check connections")

    # print graph to see connections
    print("Graph:")
    print(graph.get())
    print("--------------------")

    # Run graph
    print("Running graph if it is valid...")
    if is_valid:
        graph.execute(params)
    print("--------------------")

    # Delete graph
    print("Deleting graph...")
    graph.delete()
    print("--------------------")

    # delete user
    print("Deleting user...")
    user.delete()
    print("--------------------")