"""
A simple script to regurgitate logged housekeeping_pow packets back to a remote IP address for testing.
"""


import socket, sys, time, os

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("use like this:\n\t> python power_send.py path/to/housekeeping_pow.log -y\n (the -y flag is optional, it will send Ping packets if set)")
        sys.exit(1)
    
    local_addr = "127.0.0.1"
    local_port = 9999
    send_addr = "224.1.1.118"
    send_port = 9999

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((local_addr, local_port))
    
    with open(os.path.join(sys.argv[1], "housekeeping_pow.log"), 'rb') as file:
        power_data = file.read()
    
    ping_flag = False
    if len(sys.argv) > 2:
        with open(os.path.join(sys.argv[1], "housekeeping_ping.log"), 'rb') as file:
            ping_data = file.read()
            ping_flag = True

    print('sending...')
    power_prefix = bytes([0x02, 0x00, 0x01, 0x00, 0x01, 0x11, 0x00, 0x00])
    ping_prefix = bytes([0x02, 0x00, 0x01, 0x00, 0x01, 0x20, 0x00, 0x00])

    sleep_time = 0.1

    if ping_flag:
        for power_packet, ping_packet in zip(chunks(power_data, 0x26), chunks(ping_data, 46)):
            print("sending", (power_prefix + power_packet).hex())
            sock.sendto(power_prefix + power_packet, (send_addr,send_port))
            print("sending", (ping_prefix + ping_packet).hex())
            sock.sendto(ping_prefix + ping_packet, (send_addr,send_port))

            time.sleep(sleep_time)
    else:
        for power_packet in chunks(power_data, 0x26):
            print("sending", (power_prefix + power_packet).hex())
            sock.sendto(power_prefix + power_packet, (send_addr,send_port))

            time.sleep(sleep_time)