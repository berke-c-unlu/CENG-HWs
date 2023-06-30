
from socket import *
from threading import Thread
import time
import random
from PIL import Image
import base64
import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--port', dest='port', type=int, help='Port number')
args = parser.parse_args()

port = args.port

def client(port):
    token = None
    # the connection is kept alive until client closes it.
    c = socket(AF_INET, SOCK_STREAM)
    c.connect(('127.0.0.1', port))
    while True:
        try:

            reply = c.recv(65536).decode()
            print(c.getsockname(), reply)

            if reply.split(" ")[0] == "token":
                token = reply.split(" ")[1]
                inp = input("Enter command: ")
                if token:
                    inp += " " + token
                c.send(inp.encode())                

            elif reply.split(" ")[0] == "load_image_request":
                img_path = input("Enter image path for node {}: ".format(reply.split(" ")[1]))
                with open(img_path, "rb") as f:
                    img = base64.b64encode(f.read()).decode()

                img_dict = {"img": img}

                img_json = json.dumps(img_dict)

                #size of img_json
                c.send(str(len(img_json)).encode())

                #wait for ack
                c.recv(1024)

                #send img_json
                c.send(img_json.encode())

                print("Image sent.")
            elif reply.split(" ")[0] == "save_image_request":
                img_path = input("Enter image path to save for node {}: ".format(reply.split(" ")[1]))
                c.send(img_path.encode())
                print("Image saved.")
            elif reply.split(" ")[0] == "integer_request":
                inp = input("Enter integer for node {}: ".format(reply.split(" ")[1]))
                c.send(inp.encode())
                print("Integer sent.")
            elif reply.split(" ")[0] == "float_request":
                inp = input("Enter float for node {}: ".format(reply.split(" ")[1]))
                c.send(inp.encode())
                print("Float sent.")
            else:
                inp = input("Enter command: ")
                if token:
                    inp += " " + token
                c.send(inp.encode())
                if inp == "exit":
                    break
        except Exception as e:
            if type(e) == EOFError:
                break
            print(e)

    c.close()





cl = Thread(target = client, args=(port,))
cl.start()
