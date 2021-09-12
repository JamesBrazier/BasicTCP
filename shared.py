from io import FileIO
from socket import socket
from os import SEEK_END

class AppError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


def addrToStr(address : tuple) -> str:
    return f"{address[0]}:{address[1]}"


def bytesToStr(data : bytearray) -> str:
    string = "bytearray("

    for byte in data:
        string += '\\' + hex(byte)[1:]

    string += ')'
    return string


def shortToBytes(short : int) -> tuple:
    return (short & 0xff00) >> 8, short & 0xff


def bytesToShort(byteA : int, byteB : int) -> int:
    return (byteA << 8) | byteB


def intToBytes(integer : int) -> tuple:
    return (
        (integer & 0xff000000) >> 24, 
        (integer & 0xff0000) >> 16, 
        (integer & 0xff00) >> 8,
        integer & 0xff
    )


def bytesToInt(byteA : int, byteB : int, byteC : int, byteD : int) -> int:
    return (byteA << 24) | (byteB << 16) | (byteC << 8) | byteD


def shutdown(socket : socket):
    socket.close()
    exit()


def createFileReq(filename : str) -> bytearray:
    filename = filename.encode("utf-8")
    filenameLen = len(filename)

    if filenameLen > 2043:
        raise AppError(f"Given filename is too long")

    data = bytearray(5)

    data[0] = 0x49 #MagicNo 1st byte
    data[1] = 0x7e #2nd byte
    data[2] = 1 #type
    data[3], data[4] = shortToBytes(filenameLen)
    data += filename

    return data


def unpackFileReq(data : bytes) -> str:
    if len(data) < 5:
        raise AppError("Recieved packet is too short to be a file request")
    if data[0] != 0x49 or data[1] != 0x7e:
        raise AppError("Receieved file request is invalid")
    if data[2] != 1:
        raise AppError("Received packet is not a file request")

    filenameLen = bytesToShort(data[3], data[4])
    filename = data[5:]

    if len(filename) != filenameLen:
        raise AppError("Recieved filename of unexpected length")

    return str(filename, "utf-8")


def createFileRes(file : FileIO) -> bytearray:
    data = bytearray(8)

    data[0] = 0x49
    data[1] = 0x7e
    data[2] = 2

    if file != None:
        data[3] = 1

        file.seek(0, SEEK_END)
        data[4], data[5], data[6], data[7] = intToBytes(file.tell())
        file.seek(0, 0)

    return data


def unpackFileRes(data : bytes) -> bytes:
    if len(data) < 8:
        raise AppError("Recieved packet is too short to be a file response")
    if data[0] != 0x49 or data[1] != 0x7e:
        raise AppError("Receieved file response is invalid")
    if data[2] != 2:
        raise AppError("Received packet is not a file response")
    if data[3] != 1:
        if data[3] != 0:
            raise AppError("Receieved packet has an invalid status code")
        raise AppError("The server was unable to locate file")

    fileLen = bytesToInt(data[4], data[5], data[6], data[7])
    file = data[8:]

    if len(file) != fileLen:
        raise AppError("Received file data is of unexpected length")
    
    return fileLen, data[8:]


if __name__ == "__main__":
    pkt = createFileReq("Email.txt")
    print(bytesToStr(pkt))
    print(unpackFileReq(pkt))

    pkt = createFileRes(1, bytes("Hello,\n\nI am an email\n\nThanks, File", "utf-8"))
    print(bytesToStr(pkt))
    print(unpackFileRes(pkt))