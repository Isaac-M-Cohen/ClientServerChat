import socket
import select
import kbhit_for_mac as msvcrt #instead of importing msvcrt for windows
import Chat_Protocol as cprot
# NAME <name> will set name. Server will reply error if duplicate
# GET_NAMES will get all names
# MSG <NAME> <message> will send message to client name or to broadcast
# BLOCK <name> will block a user from sending messages to the client who sent the block command
# EXIT will close client


my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
my_socket.connect(("127.0.0.1", cprot.PORT))

msg = ""

print("Enter commands\n>", end="", flush=True)
while True:

    # Check for incoming server messages
    rlist, _, _ = select.select([my_socket], [], [], 0.2)
    if rlist:
        data = cprot.recv_msg(my_socket)
        if not data:
            print("\nERROR Server disconnected")
            break
        print("\n" + data)
        print(">" + msg, end="", flush=True)

    # Check for keyboard input
    if msvcrt.kbhit():
        ch = msvcrt.getch()

        # Enter pressed → send message
        if ch in ("\r", "\n"):
            if msg.upper() == "EXIT":
                my_socket.send(cprot.create_msg("EXIT"))
                break
            my_socket.send(cprot.create_msg(msg))
            msg = ""    # clear typed message
            #print("\n>", end="", flush=True)

        # Normal character typed
        else:
            msg += ch
            print(ch, end="", flush=True)

my_socket.close()
