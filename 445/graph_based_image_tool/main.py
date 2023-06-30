from components import *
import User
import Graph
from PIL import Image
import os



if __name__ == "__main__":
    if not os.path.exists("outputs"):
        os.makedirs("outputs")

    ##### TESTS #####


    # Create a user
    user = User.User("testuser","asd@asd.com", "12345678", "12345678")

    # Create a graph
    graph = Graph.Graph("testgraph",user)

    # Create nodes
    graph.newnode(LoadImage.LoadImage)
    graph.newnode(Crop.Crop)
    for i in range(4):
        graph.newnode(GetInteger.GetInteger)
    graph.newnode(SaveImage.SaveImage)
    graph.newnode(GetFloat.GetFloat)
    graph.newnode(Rotate.Rotate)

    # Connect nodes
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
    # Rotate -> SaveImage
    graph.connect(keys[8], "output", keys[6], "input")

    print(graph)

    print(graph.getcomponenttypes())

    params = graph.runparams()
    print(params)
    is_valid = graph.isvalid()

    if is_valid == False:
        print("Invalid graph, please check the connections or the parameters")
        exit()
    
    graph.execute(params)