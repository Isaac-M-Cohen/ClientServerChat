import socket
import select
import Chat_Protocol as cprot

# NAME <name> will set name. Server will reply error if duplicate
# GET_NAMES will get all names
# MSG <NAME> <message> will send message to client name or to broadcast
# BLOCK <name> will block a user from sending messages to the client who sent the block command
# EXIT will close client

SERVER_PORT = cprot.PORT
SERVER_IP = "0.0.0.0"


def handle_client_request(current_socket, clients_names, blocked, data):

    #Find Sender Name
    sender_name = clients_names.get(current_socket)
    splitData = data.strip().split(' ', 2)
    cmd = splitData[0].upper() if splitData else ''
    reply = 'ERROR unknown command'
    dest_socket = current_socket

    if cmd == 'NAME':
        if len (splitData) < 2:
            reply = 'ERROR blank name'
        else:
            name = splitData[1]
            if name in clients_names.values():
                reply = 'ERROR name taken'
            elif name.upper() == 'BROADCAST':
                reply = 'ERROR invalid name'
            else:
                clients_names[current_socket] = name
                blocked[current_socket] = set()
                reply = f'Hello {name}'

    elif cmd == 'GET_NAMES':
        all_names = ', '.join(clients_names.values())
        reply = all_names

    elif cmd == 'MSG':
        if len(splitData) < 3:
            reply = 'ERROR unknown command'
        else:
            target = splitData[1]
            message = splitData[2]
            if sender_name is None:
                reply = 'ERROR no name chosen'
            elif target.upper() == 'BROADCAST':
                for sock, name in clients_names.items():
                    if sock != current_socket and current_socket not in blocked[sock]:
                        msg = f'FROM {sender_name} {message}'
                        sock.send(cprot.create_msg(msg))
                reply = 'Message sent'
            else:
                if target in clients_names.values(): 
                        for sock, name in clients_names.items():
                            if name == target:
                                if current_socket not in blocked[sock]:
                                    msg = f'FROM {sender_name} {message}'
                                    sock.send(cprot.create_msg(msg))
                                    reply = f'Message sent'
                                    break
                                else:
                                    reply = f'ERROR {target} blocked you'
                else:
                    reply = f'ERROR {target} does not exist'

    elif cmd == 'BLOCK':
        if len(splitData) < 2:
            reply = 'ERROR unknown command'
        else:
            target = splitData[1]
            if sender_name is None:
                reply = 'ERROR no name chosen'
            elif target not in clients_names.values():
                reply = f'ERROR {target} does not exist'
            else:
                for sock, name in clients_names.items():
                    if name == target:
                        blocked[current_socket].add(sock)
                        reply = f'Successfully blocked {target}'
    elif cmd == 'EXIT':
        reply = 'BYE'

    return reply, dest_socket


def print_client_sockets(client_sockets):
    for c in client_sockets:
        print("\t", c.getpeername())


def main():
    print("Setting up server")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_IP, SERVER_PORT))
    print("Listening for clients")
    server_socket.listen()
    client_sockets = []
    messages_to_send = []
    clients_names = {} #"socket":"name"
    blocked = {}
    ''' {   
    "socket1": {"socket2", "socket23"} 
    "socket2": {"socket1", "socket3", "socket4"} 
    }
    '''
    while True:
        read_list = client_sockets + [server_socket]
        ready_to_read, ready_to_write, in_error = select.select(read_list, client_sockets, [])
        for current_socket in ready_to_read:
            if current_socket is server_socket:
                client_socket, client_address = server_socket.accept()
                print("Client joined!\n", client_address)
                client_sockets.append(client_socket)
                print_client_sockets(client_sockets)
            else:
                print("Data from client\n")
                data = cprot.recv_msg(current_socket)
                if data == "":
                    print("Connection closed\n")
                    disconnected_name = clients_names.pop(current_socket, None)
                    blocked.pop(current_socket, None)
                    client_sockets.remove(current_socket)
                    current_socket.close()
                    print(f"{disconnected_name} disconnected\n")
                else:
                    print(data)
                    (response, dest_socket) = handle_client_request(current_socket, clients_names, blocked, data)
                    messages_to_send.append((dest_socket, response))

        # write to everyone (note: only ones which are free to read...)
        for message in messages_to_send:
            current_socket, data = message
            if current_socket in ready_to_write:
                response = cprot.create_msg(data)
                current_socket.send(response)
                messages_to_send.remove(message)


if __name__ == '__main__':
    main()