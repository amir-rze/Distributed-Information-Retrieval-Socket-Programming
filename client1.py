import socket
import pickle
import threading

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('localhost', 12345)
client_socket.connect(server_address)
client_socket.settimeout(5.0)
client_id = 1
client_socket.send(str(client_id).encode())
data = b""
while True:
    try:
        packet = client_socket.recv(4096)
    except :
        break
    if not packet:
         break
    data += packet
data = pickle.loads(data)
print(f"client#{client_id} :  dataset received from server.")
client_socket.settimeout(None)



def receive_message(socket):
    message_length = int.from_bytes(socket.recv(4), byteorder="big") 
    data = b""
    while len(data) < message_length:
        chunk = socket.recv(4096)
        if not chunk:
            break
        data += chunk
    return data

def send_message(socket, message):
    message_length = len(message)
    socket.sendall(message_length.to_bytes(4, byteorder="big"))
    socket.sendall(message)

def client_receive():
     while True :    
        try:
            response = receive_message(client_socket)
            if not response:
                print("Disconnected from the server.")
                break
            response = pickle.loads(response)
        except Exception as e:
            print(f"Error! : {e}")
            break
        if 'data' in response:
            print("\nremaining data catched from other clients via server : \n")
            print(response['data'])
        else :
            info = []
            for d in data:
                if d["'id'"][1:-1] in response['id_list']:
                    info.append(d)
            dic = {"requested_client_id" : response["requested_client_id"] , "data":info}
            send_message(client_socket, pickle.dumps(dic))

def client_send():
    while True:
        command = input("\nType your command? (yes : (To write list of id seprated with a space) / show : (showing result if existed) /exit)\n")
        if command=="exit" : 
            break
        elif command == "yes":
            id_str = input("Enter ID list: \n")
            id_list = id_str.split()
            temp_list = id_list
            for d in data:
                if d["'id'"][1:-1] in temp_list:
                    print()
                    print(d)
                    id_list.remove(d["'id'"][1:-1])
            if len(id_list) != 0 :
                dic = {"requested_client_id" : str(client_id) , 
                "id_list" : id_list
                }
                send_message(client_socket, pickle.dumps(dic))
                print("remaining ids sent to server , please wait to catch data... (if you want to show response please type 'show')")
        else:
            continue
       

receive_thread = threading.Thread(target=client_receive)
receive_thread.start()

send_thread = threading.Thread(target=client_send)
send_thread.start()