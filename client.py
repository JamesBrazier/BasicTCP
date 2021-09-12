from sys import argv
from socket import *
from pathlib import Path
from shared import *
from os import remove

def getCLArgs():
    if len(argv) != 4 or not argv[2].isdigit():
        raise AppError("Usage: client.py <address> <port> <file>\n\n\taddress: the ip address/hostname of the host to connect to\n\n\tport: an integer value between 1024 and 64000, inclusive\n\n\tfile: the path to the file to send")

    port = int(argv[2])

    if port < 1024 or port > 64000:
        raise AppError(f"The given port {port} is not an integer between 1024 and 64000, inclusive")

    file = argv[3]

    #if Path(file).is_file():
    #    raise AppError(f"File '{file}' already exists")

    try:
        addrInfo = getaddrinfo(argv[1], port, AF_INET, SOCK_STREAM)
    except OSError:
        raise AppError(f"Host at {argv[1]} can't be reached")

    return addrInfo[0][4], file


def main():
    try:
        address, file = getCLArgs()

        print(f"Connecting to {addrToStr(address)}...")
        with socket(AF_INET, SOCK_STREAM) as connection:
            connection.settimeout(1)
            connection.connect(address)

            print(f"Connected, requesting file '{file}'...")
            pkt = createFileReq(file)
            connection.send(pkt)

            pkt = connection.recv(4096)
            dataLen, data = unpackFileRes(pkt)
            dataFile = f"data{file[file.rfind('.'):]}"
            
            with open(dataFile, "wb") as fileObj:
                fileObj.write(data)
                recvdData = len(data)

                while recvdData < dataLen:
                    print(f"Recieved {(recvdData / dataLen) * 100 :.1f}% ({recvdData}/{dataLen} bytes)...", end='\r')
                    data = connection.recv(4096)
                    fileObj.write(data)
                    recvdData += len(data)

                if recvdData != dataLen:
                    print(f"Receieved an unexpected number of bytes, deleting {file}...")
                    fileObj.truncate(0)
                    fileObj.close()
                    remove(dataFile)

            print(f"File '{file}' (size: {recvdData} bytes) recieved successfully")
            
        print("Connection closed")
            
    except (OSError, AppError) as err:
        print(f"\n{err}\n")


main()