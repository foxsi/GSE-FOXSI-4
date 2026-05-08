import sys, socket, random, ipaddress, struct, time

structure = {
    0x0e: {
        0x00: {"length": 0x90400, "frame_counter": 0},
        0x01: {"length": 0x78400, "frame_counter": 0}
    },
    0x0f: {
        0x00: {"length": 0x90400, "frame_counter": 0},
        0x01: {"length": 0x78400, "frame_counter": 0}
    },
    0x09: {
        0x00: {"length": 0x800c, "frame_counter": 0}
    },
    0x0a: {
        0x00: {"length": 0x800c, "frame_counter": 0}
    },
    0x0b: {
        0x00: {"length": 0x800c, "frame_counter": 0}
    },
    0x0c: {
        0x00: {"length": 0x800c, "frame_counter": 0}
    }
}

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

max_payload = 1440

def make_packets(system:int, data:int):
    counter_value = structure[system][data]["frame_counter"]
    counter_value = counter_value & 0xffff # wrap to 16 bits
    
    # put the 16-bit counter as the payload of the whole frame, repeating.
    frame = [(counter_value >> 8) & 0xff if k % 2 == 0 else counter_value & 0xff for k in range(structure[system][data]["length"])]
    # frame = [0x01 if counter_value % 2 == 0 else 0x10 for k in range(structure[system][data]["length"])]
    total_packets = -(-structure[system][data]["length"] // max_payload)
    
    packets = []
    # print(chunks(frame, max_payload))
    for k,p in enumerate(chunks(frame, max_payload)):
        header = [
            system & 0xff, 
            (total_packets >> 8) & 0xff, total_packets & 0xff,
            ((k+1) >> 8) & 0xff, (k+1) & 0xff,
            data & 0xff,
            (counter_value >> 8) & 0xff, counter_value & 0xff
        ]
        header.extend(p)
        # put the header on this packet, then put the whole thing in the list of packets.
        packets.append(header)
    structure[system][data]["frame_counter"] = 1 + structure[system][data]["frame_counter"]
    return packets

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("use like this:\n\t> python send_frames.py local-ip local-port send-ip send-port")
        sys.exit(1)
    
    local_addr = sys.argv[1]
    local_port = int(sys.argv[2])
    forward_addr = sys.argv[3]
    forward_port = int(sys.argv[4])
    
    intermediate_addr = "127.0.0.1"
    
    if ipaddress.IPv4Address(local_addr).is_multicast:
        listen_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        listen_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

        listen_sock.bind((local_addr, local_port))
        # if ipaddress.IPv4Address(forward_addr).is_multicast:
        #     mreq = struct.pack('4s4s', socket.inet_aton(local_addr), socket.inet_aton(intermediate_addr))
        #     listen_sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    else:
        listen_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        listen_sock.bind((local_addr, local_port))

    print('listening...')
    while True:
        for system in structure.keys():
            for data in structure[system].keys():
                
                packets = make_packets(system, data)
                print("system", hex(system), "type", hex(data), "\033[0;1mframe count", hex(structure[system][data]["frame_counter"]), "\033[0msending", len(packets), "packets")
                for packet in packets:
                    listen_sock.sendto(bytes(packet), (forward_addr, forward_port))
                time.sleep(0.25)