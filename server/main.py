import socket
import threading
from handler import handle_client
from database import load_users

HOST = '0.0.0.0'
PORT = 12345

users = load_users()

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()
print(f"[LISTENING] Server running on {HOST}:{PORT}")

while True:
    conn, addr = server.accept()
    thread = threading.Thread(target=handle_client, args=(conn, addr, users))
    thread.start()
