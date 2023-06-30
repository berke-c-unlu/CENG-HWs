from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from socket import *
import json
import base64
# Create your views here.

port = 20446

def index(request):
    c = socket(AF_INET, SOCK_STREAM)
    c.connect(('127.0.0.1', port))
    c.recv(65536)

    msg = "list" + " " + (request.COOKIES['token'] if 'token' in request.COOKIES else "not_logged_in")

    c.send(msg.encode())

    reply = c.recv(1024).decode()
    try:
        graphs = json.loads(reply)["graphs"]
        opened_graph = json.loads(reply)["opened"]
    except:
        graphs = []
        opened_graph = ""

    if request.method == "POST":
        if 'login_button' in request.POST:
            print(request.COOKIES)
            if 'token' in request.COOKIES:
                print("Already logged in.")
                request.session['error'] = "Already logged in."
                return redirect("index")

            c = socket(AF_INET, SOCK_STREAM)
            c.connect(('127.0.0.1', port))
            c.recv(65536)

            msg = "login " + request.POST['username'] + " " + request.POST['passwd']

            c.send(msg.encode())

            reply = c.recv(1024).decode()
            print("server said: " + reply)
            reply = reply.split(" ")
            if reply[0] == "token":
                token = reply[1]
                response = redirect("index")
                response.set_cookie(key="token", value=token)
                request.session['success'] = "Successfully logged in."
                return response
            else:
                request.session['error'] = "Login failed."
                print("Login failed.")

        elif 'register_button' in request.POST:
            print(request.COOKIES)
            if 'token' in request.COOKIES:
                print("Already logged in.")
                return redirect("index")

            c = socket(AF_INET, SOCK_STREAM)
            c.connect(('127.0.0.1', port))
            c.recv(65536)

            msg = "register " + request.POST['username'] + " " + request.POST['passwd'] + " " + request.POST['email'] + " " + request.POST['fullname']

            c.send(msg.encode())

            reply = c.recv(1024).decode()
            reply = reply.split(" ")
            print("server said: ", reply)

            if reply[0] == "registered":
                request.session['success'] = "Successfully registered."
                return redirect("index")
            else:
                request.session['error'] = "Registration failed."
                print("Registration failed.")

        elif 'logout_button' in request.POST:
            if 'token' not in request.COOKIES:
                print("Not logged in.")
                request.session['error'] = "You are not logged in."
                return redirect("index")

            token = request.COOKIES['token']

            msg = "logout " + token

            c = socket(AF_INET, SOCK_STREAM)
            c.connect(('127.0.0.1', port))
            c.recv(65536)

            c.send(msg.encode())

            reply = c.recv(1024).decode()
            print("server said: " + reply)

            response = redirect("index")
            response.delete_cookie("token")
            return response

        elif 'add_graph_button' in request.POST:
            if 'token' not in request.COOKIES:
                print("Not logged in.")
                request.session['error'] = "You are not logged in."
                return redirect("index")

            token = request.COOKIES['token']

            msg = "new " + request.POST['graph_name'] + " " + token

            c = socket(AF_INET, SOCK_STREAM)
            c.connect(('127.0.0.1', port))
            c.recv(65536)

            c.send(msg.encode())

            reply = c.recv(1024).decode()
            if reply.startswith("something"):
                request.session['error'] = reply.split(":")[1]
            else:
                request.session['success'] = "Graph is successfully created."
            print("server said: " + reply)

        elif 'open_graph_button' in request.POST:
            if 'token' not in request.COOKIES:
                print("Not logged in.")
                request.session['error'] = "You are not logged in."
                return redirect("index")

            token = request.COOKIES['token']

            msg = "open " + request.POST['open_graph_button'] + " rw " + token

            c = socket(AF_INET, SOCK_STREAM)
            c.connect(('127.0.0.1', port))
            c.recv(65536)

            c.send(msg.encode())

            reply = c.recv(1024).decode()
            if reply.startswith("something"):
                request.session['error'] = reply.split(":")[1]
            else:
                request.session['success'] = "Graph "+ request.POST['open_graph_button'] +" is opened."

        elif 'close_graph_button' in request.POST:
            if 'token' not in request.COOKIES:
                print("Not logged in.")
                request.session['error'] = "You are not logged in."
                return  redirect("index")

            token = request.COOKIES['token']

            msg = "close " + token

            c = socket(AF_INET, SOCK_STREAM)
            c.connect(('127.0.0.1', port))
            c.recv(65536)

            c.send(msg.encode())

            reply = c.recv(1024).decode()
            if reply.startswith("something"):
                request.session['error'] = reply.split(":")[1]
            else:
                request.session['success'] = "Graph is closed."
            print("server said: " + reply)
                     

        elif 'add_component_button' in request.POST:
            if 'token' not in request.COOKIES:
                print("Not logged in.")
                return redirect("index")

            token = request.COOKIES['token']

            msg = "add " + request.POST['component_type'] + " " + token

            c = socket(AF_INET, SOCK_STREAM)
            c.connect(('127.0.0.1', port))
            c.recv(65536)

            c.send(msg.encode())

            reply = c.recv(1024).decode()
            print("server said: " + reply)
            if reply.startswith("something"):
                request.session['error'] = reply.split(":")[1]
            else:
                request.session['success'] = request.POST['component_type']+" component is added."
        
        elif 'connect_nodes_button' in request.POST:
            if 'token' not in request.COOKIES:
                print("Not logged in.")
                return redirect("index")

            token = request.COOKIES['token'] 

            msg = "connect " + request.POST["node1"] + " " + request.POST["outports_connect"] + " " + request.POST["node2"] + " " + request.POST["inports_connect"] + " " + token 

            c = socket(AF_INET, SOCK_STREAM)
            c.connect(('127.0.0.1', port))
            c.recv(65536)

            c.send(msg.encode())

            reply = c.recv(1024).decode()
            print("server said: " + reply)
            if reply.startswith("something"):
                request.session['error'] = reply.split(":")[1]
            else:
                request.session['success'] = request.POST["node1"] + "s " + request.POST["outports_connect"] + " is connected to " + request.POST["node2"] + "s " + request.POST["inports_connect"] + "."
        
        elif 'disconnect_nodes_button' in request.POST:
            if 'token' not in request.COOKIES:
                print("Not logged in.")
                return redirect("index")

            token = request.COOKIES['token']    

            msg = "disconnect " + request.POST["node1"] + " " + request.POST["outports_disconnect"] + " " + request.POST["node2"] + " " + request.POST["inports_disconnect"] + " " + token 

            c = socket(AF_INET, SOCK_STREAM)
            c.connect(('127.0.0.1', port))
            c.recv(65536)

            c.send(msg.encode())

            reply = c.recv(1024).decode()
            print("server said: " + reply)
            if reply.startswith("something"):
                request.session['error'] = reply.split(":")[1]
            else:
                request.session['success'] = request.POST["node1"] + "s " + request.POST["outports_disconnect"] + " is disconnected from " + request.POST["node2"] + "s " + request.POST["inports_disconnect"] + "."

        elif 'validate_graph_button' in request.POST:
            pass

        elif 'execute_graph_button' in request.POST:
            if 'token' not in request.COOKIES:
                print("Not logged in.")
                return redirect("index")

            token = request.COOKIES['token']  

            msg = "execute " + token

            c = socket(AF_INET, SOCK_STREAM)
            c.connect(('127.0.0.1', port))
            c.recv(65536)

            c.send(msg.encode())

            r=c.recv(1024).decode()
            print("server said: " + r)

            data = {}

            for key in request.POST:
                if key.startswith("save_image") or key.startswith("get_float") or key.startswith("get_integer"):
                    id = key.split("_")[-1]
                    data[id] = request.POST[key]
            
            for key in request.FILES:
                if key.startswith("load_image"):
                    id = key.split("_")[-1]
                    data[id] = base64.b64encode(request.FILES[key].read()).decode()
            
            print(str(len(json.dumps(data))))

            c.send(str(len(json.dumps(data))).encode())

            reply = c.recv(1024).decode()

            print("server said: " + reply)

            msg = json.dumps(data)

            c.sendall(msg.encode())

            reply = c.recv(1024).decode()
            print("server said: " + reply)
            if reply.startswith("something"):
                request.session['error'] = reply.split(":")[1]
            else:
                request.session['success'] = "Graph is successfully executed."

        else:
            print("Unknown post request: " + str(request.method) + " " + str(request.body.decode()))

        return redirect("index")

    logged_in = 'token' in request.COOKIES
    if request.session.get('error'):
        error = request.session['error']
        del request.session['error']
    else:
        error = None
    if request.session.get('success'):
        success = request.session['success']
        del request.session['success']
    else:
        success = None
    return render(request, "client_app/index.html", {"logged_in":logged_in,"graphs": graphs, "opened_graph": opened_graph, "error": error, "success": success})

def send_outports(request):
    if request.method == "POST":
        if 'token' not in request.COOKIES:
            print("Not logged in.")
            return redirect("index")

        node_id = json.loads(request.body.decode())["nodeid"]

        token = request.COOKIES['token']  

        msg = "outports " + str(node_id) + " "  + token

        c = socket(AF_INET, SOCK_STREAM)
        c.connect(('127.0.0.1', port))
        c.recv(65536)

        c.send(msg.encode())

        reply = c.recv(1024).decode()
        print("server said: " + reply)

        try:
            reply = json.loads(reply)
        except:
            reply = {
                'outports': None,
                'inports': None
            }

        return JsonResponse(reply, safe=False)

    return redirect("index")


