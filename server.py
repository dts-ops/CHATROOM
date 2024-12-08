import socket
import threading
import json

def close_server():
    global stop_server
    boardcast('/r'.encode(FORMAT)) 
    stop_server = True
    server.close()
    raise SystemExit(0)


def console():
    while True:
        i = input('>').lower()
        t = ['quit','exit','list']
        if i in t:
            if t.index(i) == 0 or t.index(i) == 1: # Tạo chương trình đóng
                close_server()
                raise SystemExit(0)
                
            elif t.index(i) == 2:
                for k in range(len(nicknames)):
                    print(f'[CLIENT] {clients[k]} [NICKNAME] {nicknames[k]}')

def boardcast(msg):
    for client in clients:
        client.send(msg)

def receive(): # Nhập kết nối từ mọi client và sử lí nickname
    while not stop_server:
        try:
            client, address = server.accept()
            print(f'[CONNECTED] Connected to {str(address)}')

            client.send('/n'.encode(FORMAT))
            nickname = client.recv(1024).decode(FORMAT)

            if nickname in nicknames or nickname == '':
                client.send('/nr'.encode(FORMAT))
                client.close()
            else:
                nicknames.append(nickname)
                clients.append(client)
                boardcast(f'Chào mừng ngường dùng {nickname} đã tham gia chatroom.'.encode(FORMAT))
                thread_handle = threading.Thread(target = handle,args = (client,))
                thread_handle.start()
        except ConnectionAbortedError:
            break

def close_client(client):
    index = clients.index(client)
    print(f'[DISCONNECTED] Client {nicknames[index]}')
    nicknames.remove(nicknames[index])
    clients.remove(clients[index])

def handle(client): # Nhận tin nhắn từ các client
    while not stop_server:
        try:
            msg = client.recv(1024).decode(FORMAT)
            if msg:
                if msg == '/r': # Nhận được yêu cầu client đã đóng
                    close_client(client)
                else:
                    boardcast(msg.encode(FORMAT))
        except:
            close_client(client)
            print(f'[DISCONNECTED] Client {nicknames[clients.index(client)]}')

# Cấu hình server
with open('config.json','r') as f:
    p = json.load(f)
    HOST = p['ip']  # Địa chỉ localhost
    PORT = p['port']        # Cổng để giao tiếp

if not HOST or not PORT:
    print('[ERROR] PLease check again config file')
    raise SystemExit(0)
stop_server = False

print(f"[RUNNING] The server is running at {HOST}:{PORT}")

FORMAT = 'utf-8'
ADDRESS = (HOST,PORT)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    server.bind(ADDRESS)
except:
    print("[SERVER] Cann't starting server")
    raise SystemExit(0)

server.listen()

clients = []
nicknames = []

thread_console = threading.Thread(target = console)
thread_receive = threading.Thread(target = receive)

thread_receive.start()
thread_console.start()
