import traceback

from spawnitem import send_item, UDP_IP, UDP_PORT
import socket
import json
from cctypes import *


def create_client() -> None:
    # Create a TCP/IP socket
    client_socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_addr: tuple[str, int] = ('localhost', 58432)
    client_socket.connect(server_addr)
    print(f"Listening for effects from server {server_addr[0]} on port {server_addr[1]}")
    print(f"Sending effects to client {UDP_IP} on port {UDP_PORT}")

    buffer: bytes = b""
    while True:
        # Receive data from the server
        data: bytes = client_socket.recv(1024)
        if not data:
            break

        buffer += data
        while b'\x00' in buffer:
            # Split the buffer by the null byte
            message: bytes
            message, buffer = buffer.split(b'\x00', 1)
            print("Received message:", message)

            # Decode the message
            json_data: str = message.decode('utf-8')
            request: Request = json.loads(json_data)

            # Check if the request is a start effect request
            if request["type"] != RequestType.START.value:
                continue
            if "code" not in request:
                continue

            # Execute the effect
            code: list[str] = request["code"].lower().split("_", 1)
            response: Response = {"id": request["id"], "type": ResponseType.EFFECT_REQUEST.value, "code": request["code"]}
            try:
                match code[0]:
                    case "spawnitem":
                        send_item(code[1], response)
                    case _:
                        print("Unknown code:", code[0])
                        response["status"] = EffectStatus.UNAVAILABLE.value
            except:
                print("Encountered an error while trying to execute an effect")
                traceback.print_exc()
                response["status"] = EffectStatus.RETRY.value

            print("Sending response:", response)

            # Convert the dictionary to a JSON string and add the suffix
            response_json: str = json.dumps(response) + '\x00'

            # Send the data back to the server
            client_socket.sendall(response_json.encode('utf-8'))

    client_socket.close()


if __name__ == '__main__':
    create_client()
