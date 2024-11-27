"""
Get in loser. We're dropping packets.

This is an (un)helpful (dis)utility to ingest downlink packets and
randomly drop some of them. Can use to stress-test the logging
capability of the GSE.

You may need to mess with addresses in `foxsi4-commands/systems.json` to
get this to be useful. One way to do this would be to change
`systems.json`'s Ethernet address property for the gse system:
    gse.ethernet_interface.address : "127.0.0.120"
And to delete the line
    "mcast_group": "224.1.1.118"
from `system.json`. So the resultant "gse" block would contain this
"ethernet_interface":

.. code-block:: json

    "ethernet_interface": {
            "protocol": "udp", "address": "127.0.0.120", "port": 9999,
            "max_payload_bytes": 2000
        },

Then run `packet_loser.py` like this:
    > python packet_loser.py 224.1.1.118 9999 127.0.0.120 9999 0.3333

This will get `packet_loser.py` to listen on the usual downlink
broadcast IP and port: 224.1.1.118:9999, drop 1/3 packets randomly, and
retransmit to the local IP address and port 127.0.0.120:9999.

If you then launch the GSE with your modified
`foxsi4-commands/systems.json` file (which sets the GSE address to )
"""

import sys, socket, random, ipaddress, struct

if __name__ == "__main__":
    if len(sys.argv) != 6:
        print("use like this:\n\t> python packet_loser.py listen-ip listen-port send-ip send-port drop-rate")
        sys.exit(1)
    
    listen_addr = sys.argv[1]
    listen_port = int(sys.argv[2])
    forward_addr = sys.argv[3]
    forward_port = int(sys.argv[4])

    intermediate_addr = "127.0.0.1"

    drop_odds = float(sys.argv[5])

    if ipaddress.IPv4Address(listen_addr).is_multicast:
        listen_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        listen_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

        listen_sock.bind((listen_addr, listen_port))
        if not ipaddress.IPv4Address(forward_addr).is_multicast:
            mreq = struct.pack('4s4s', socket.inet_aton(listen_addr), socket.inet_aton(forward_addr))
        else:
            mreq = struct.pack('4s4s', socket.inet_aton(listen_addr), socket.inet_aton(intermediate_addr))

        listen_sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    else:
        listen_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        listen_sock.bind((listen_addr, listen_port))

    print('listening...')
    while True:
        data, sender = listen_sock.recvfrom(4096)
        if random.random() > drop_odds:
            listen_sock.sendto(data, (forward_addr, forward_port))
