"""
A simple script to regurgitate logged housekeeping_pow packets back to a remote IP address for testing.
"""


import socket, sys, time

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("use like this:\n\t> python power_send.py path/to/housekeeping_pow.log")
        sys.exit(1)
    
    local_addr = "127.0.0.1"
    local_port = 9999
    send_addr = "224.1.1.118"
    send_port = 9999

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((local_addr, local_port))
    
    with open(sys.argv[1], 'rb') as file:
        data = file.read()

    print('sending...')
    prefix = bytes([0x02, 0x00, 0x01, 0x00, 0x01, 0x11, 0x00, 0x00])
    for chunk in chunks(data, 0x26):
        print("sending", (prefix + chunk).hex())
        sock.sendto(prefix + chunk, (send_addr,send_port))
        time.sleep(0.5)