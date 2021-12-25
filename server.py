from sys import argv
from socket import *
from datetime import datetime
from time import sleep
from shared import *

def getPort():
    if len(argv) != 2 or not argv[1].isdigit():
        raise AppError("Usage: server.py <port>\n\n\tport: an integer value between 1024 and 64000, inclusive")

    port = int(argv[1])

    if port < 1024 or port > 64000:
        raise AppError(f"The given port {port} is not an integer between 1024 and 64000, inclusive")

    return port


def main():
    try:
        port = getPort()

        server = None
        server = socket(AF_INET, SOCK_STREAM)
        server.bind(("", port))
        server.listen()
        server.setblocking(False)
        print(f"Server listening on port {port}...")

        while True:
            try:
                connection, address = server.accept()
                with connection:
                    connection.settimeout(1)
                    print(f"Accepted connection from {addrToStr(address)} at {datetime.now()}")

                    pkt = connection.recv(2048)
                    file = unpackFileReq(pkt)
                    print(f"Recieved file request from {addrToStr(address)} for {file}, reading...")

                    try:
                        with open(file, 'rb') as file:
                            print("File successfully read")

                            connection.send(createFileRes(file))

                            data = file.read(4096)
                            connection.send(data)
                            while len(data) != 0:
                                data = file.read(4096)
                                connection.send(data)

                    except FileNotFoundError:
                        print(f"File not found")
                        connection.send(createFileRes(None))

                    print(f"Response sent to {addrToStr(address)}...")

                print(f"Connection {addrToStr(address)} closed")

            except BlockingIOError:
                sleep(server, 0.1)
                continue

            except (OSError, AppError) as err:
                print(f"\nConnection error: {err}\n")
                continue
        
    except (OSError, KeyboardInterrupt) as err:
        if socket != None:
            socket.close()
        print(f"\n{err}\n")
        exit()


main()
