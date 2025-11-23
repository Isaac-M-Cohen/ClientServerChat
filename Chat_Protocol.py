# NAME <name> will set name. Server will reply error if duplicate
# GET_NAMES will get all names
# MSG <NAME> <message> will send message to client name or to broadcast
# BLOCK <name> will block a user from sending messages to the client who sent the block command
# EXIT will close client

LEN_FIELD_SIZE = 3
PORT = 8200


def create_msg(data):
    # shalom -> 006shalom
    length = str(len(data)) #length of 'shalom', 6
    len_field = length.zfill(LEN_FIELD_SIZE) #fills zeros to the left, 006
    msg = len_field + data
    return msg.encode()

def recv_msg(socket):
    data_len = socket.recv(LEN_FIELD_SIZE).decode() #Can't convert to int here in case recv return ""
    if not data_len:
        return ''
    data = socket.recv(int(data_len)).decode()
    return data