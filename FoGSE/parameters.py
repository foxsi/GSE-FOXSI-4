
DEBUG = True

GSE_IP = "192.168.1.100"
GSE_PORT = 10000

FORMATTER_IP = "192.168.1.8"
FORMATTER_PORT = 9999

# commands to send to Formatter.
# todo: add applicability matrix (check sending to correct system)
MACRO_COMMANDS = [
    "PING",
    "ON",
    "OFF",
    "RESET",
    "NOTIFY_ENDFLIGHT",
    "NOTIFY_LAUNCH",
    "NOTIFY_HOLD",
    "NOTIFY_SHUTTER_OPEN",
    "NOTIFY_SHUTTER_CLOSE",
    "START_SAVING",
    "HV_SET",
    "HV_RAMPUP",
    "HV_RAMPDOWN",
    "SET_PC_EXPOSURE",
    "SET_QL_EXPOSURE",
    "READ_ADDR",
    "READ_BLOCK",
    "READ_TEMP",
    "READ_HV",
    "READ_FLAG"
]

SUBSYSTEMS = set([
    "GSE",              # use for loopback
    "FORMATTER",        # typical addressee for HOUSEKEEPING commands
    "HOUSEKEEPING",     # can address uniquely for ground test
    "CMOS1",
    "CMOS2",
    "CDTE1",
    "CDTE2",
    "CDTE3",
    "CDTE4",
    "CDTEDE",
    "TIMEPIX"
])

UPLINK_PACKET_ID_DELIM = "\t"
UPLINK_PACKET_SUBSYSTEM_DELIM = "\t"
UPLINK_PACKET_COMMAND_DELIM = "\t"

def DEBUG_PRINT(string):
    if DEBUG:
        print(string)