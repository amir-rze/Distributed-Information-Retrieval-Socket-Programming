import socket
import csv
import random
import pickle
import threading


with open("RandomData.csv", "r") as csv_file:
    csv_reader = csv.DictReader(csv_file)
    data = list(csv_reader)

client_data = {}
num_clients = 3 

random.shuffle(data)
data_per_client = len(data) // num_clients
for i in range(num_clients):
    start = i * data_per_client
    end = (i + 1) * data_per_client
    if i == num_clients-1:
        client_data[i] = data[start:len(data)]
    else:
        client_data[i] = data[start:end]

clients_dic = {}   

ThreadCount = 0
client_handler_threads = []

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

def client_handler(connection):
    while True:
        response = receive_message(connection)
        if not response:
            print("Connection closed by the client.")
            break
        data = pickle.loads(response)
        requested_client_id = data["requested_client_id"]
        if "id_list" in data:
            for key , value in clients_dic.items():
                if key == requested_client_id:
                    continue
                dic = {'requested_client_id' : requested_client_id , 'id_list' : data["id_list"]}
                send_message(value, pickle.dumps(dic))
                print(f"Server sent ID list to client #{str(key)} ")
        else:
            send_message(clients_dic[requested_client_id],response)
    connection.close()



def accept_connections(ServerSocket):
    while True:
        Client, address = ServerSocket.accept()
        print('Connected to: ' + address[0] + ':' + str(address[1]))
        client_id = Client.recv(4096).decode()
        clients_dic[client_id] = Client
        Client.sendall(pickle.dumps(client_data[int(client_id)]))
        client_handler_thread = threading.Thread(target=client_handler, args=(Client,))
        client_handler_threads.append(client_handler_thread)
        client_handler_thread.start()

def start_server(host, port):
    ServerSocket = socket.socket()
    try:
        ServerSocket.bind((host, port))
    except socket.error as e:
        print(str(e))

    print(f'Server is listing on the port {port}...')
    ServerSocket.listen(5)
    accept_connections(ServerSocket)

start_server('localhost', 12345)

