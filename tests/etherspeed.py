import socket
import time, sys

FORMATTER_IP = "192.168.1.8"
FORMATTER_PORT = 9999

BUFF_LEN = 1024

FORMATTER_HOST_IP = socket.gethostbyname("raspberrypi.local")

print("hostname matches:\t" + str(FORMATTER_IP == FORMATTER_HOST_IP))

formatter_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# formatter_sock.bind((FORMATTER_IP, FORMATTER_PORT))
# formatter_sock.connect((FORMATTER_IP, FORMATTER_PORT))

GSE_IP = "192.168.1.100"
# GSE_IP = "localhost"
GSE_PORT = 9999

gse_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
gse_sock.bind((GSE_IP, GSE_PORT))
# gse_sock.connect((GSE_IP, GSE_PORT))

# formatter_sock.sendto(b'hi there', (FORMATTER_IP, FORMATTER_PORT))
data, addr = gse_sock.recvfrom(BUFF_LEN)
# data, addr = formatter_sock.recvfrom(BUFF_LEN)
print(data)
time.sleep(1)
formatter_sock.sendto(b'y\n', (FORMATTER_IP, FORMATTER_PORT))
time.sleep(1)

# newdata, newwaddr = gse_sock.recvfrom(BUFF_LEN)
newdata, newwaddr = formatter_sock.recvfrom(BUFF_LEN)
print(newdata)

message_counter = 0
duration = 20
message_size = 0
start_time = time.time()
while time.time() - start_time <= duration:
    # data, addr = gse_sock.recvfrom(BUFF_LEN)
    data, addr = formatter_sock.recvfrom(BUFF_LEN)
    message_counter = message_counter + 1
    # print(message_counter)
    message_size = len(data)

end_time = time.time()
print("\nlast message: "+str(data))

print("\nreceived "+str(message_counter)+" messages of size "+str(message_size) +"in "+str(end_time - start_time)+" seconds")
print("incident datarate:\t"+str(8e-6*message_size*message_counter/(end_time - start_time))+" Mbps")