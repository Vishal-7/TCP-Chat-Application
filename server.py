import socket, threading

#Credentials for connection establishment
host = '127.0.0.1'
port = 55555

#Starting the server with the given credentials
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

#Clients and Nicknames
clients = []
nicknames= []

# Sending messages to all the connected clients
def broadcast(message):
    """
    Function that is used to broadcast messages to different clients connected to the server
    """
    for client in clients:
        client.send(message)

def handle(client):
    """
    Function that handles different types of messages from clients connected to the server
    """
    while True:
        try:
            msg = message = client.recv(1024)

            """ Code segment that involves with kicking out the user by a moderator """
            if message.decode('ascii').startswith("KICK"):
                if nicknames[clients.index(client)] == "admin":
                    name_to_kick = msg.decode('ascii')[5:]
                    kick_user(name_to_kick)
                else:
                    client.send("Command was refused!".encode('ascii')) # Command refused to execute as the user is not a moderator

            """ Code segment that involves with banning the user by a moderator """        
            elif message.decode('ascii').startswith("BAN"):
                if nicknames[clients.index(client)] == "admin":
                    name_to_ban = msg.decode('ascii')[4:]
                    kick_user(name_to_ban)
                    with open('bans.txt', 'a') as f:
                        f.write(f"{name_to_ban}\n")
                    print(f"{name_to_ban} was banned!")
                else:
                    client.send("Command was refused!".encode('ascii'))
            else:
                broadcast(message)
        except:
            if client in clients:
                index = clients.index(client)
                clients.remove(client)
                client.close()
                nickname = nicknames[index]
                broadcast(f"{nickname} left that chat!".encode('ascii'))
                nicknames.remove(nickname)
                break

def receive():
    while True:
        client, address = server.accept()
        print(f"Connected with {str(address)}!")

        client.send("NICK".encode('ascii'))

        nickname = client.recv(1024).decode('ascii')

        with open('bans.txt', 'r') as f:
            bans = f.readlines()

        if nickname+ '\n' in bans:
            client.send("BAN".encode('ascii'))
            client.close()
            continue
        
        if nickname == "admin":
            client.send("PASS".encode('ascii'))
            password = client.recv(1024).decode('ascii')

            if password != 'adminpass':
                client.send("REFUSE".encode('ascii'))
                client.close()
                continue

        nicknames.append(nickname)
        clients.append(client)

        print(f"Nickname is {nickname}!")
        broadcast(f"{nickname} has joined the chat!".encode('ascii'))
        client.send("Connected to the server!".encode('ascii'))

        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

def kick_user(name):
    if name in nicknames:
        name_index = nicknames.index(name)
        client_to_kick = clients[name_index]
        clients.remove(client_to_kick)
        client_to_kick.send("You were kicked by an admin!".encode('ascii'))
        client_to_kick.close()
        nicknames.remove(name)
        broadcast(f"{name} was kicked by an admin!".encode('ascii'))
        

print("Server is listening...")
receive()

    
