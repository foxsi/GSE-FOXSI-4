import socket, struct

group = "224.1.1.118"
port = 9999

local_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
local_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

local_socket.bind((group, port))
local_socket.setsockopt(socket.SOL_IP, socket.IP_ADD_MEMBERSHIP,
                    socket.inet_aton(group) + socket.inet_aton("192.168.1.118"))

while True:
    info, sender = local_socket.recvfrom(2048)
    print("received ", info, " from ", sender)