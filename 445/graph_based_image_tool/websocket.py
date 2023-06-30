import websockets
import asyncio

async def register():
    pass

async def login():
    pass

async def logout():
    pass

async def open_graph():
    pass

async def add_graph():
    pass

async def close_graph():
    pass

async def add_component():
    pass

async def connect_nodes():
    pass

async def disconnect_nodes():
    pass

async def execute_graph():
    pass

async def validate_graph():
    pass

async def main(websocket, path):
    async for message in websocket:
        print(message)

start_server = websockets.serve(main, "localhost", 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()