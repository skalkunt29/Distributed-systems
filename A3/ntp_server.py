import socket
import struct
import time

NTP_SERVER = '127.0.0.1'
NTP_PORT = 5000

NTP_PACKET_FORMAT = "!12I"
NTP_PACKET_SIZE = 48    # 12 * 4

NTP_LI = 0      # 2 bits
NTP_VN = 4      # 3 bits
NTP_MODE = 4    # 3 bits

NTP_LI_VN_MODE = NTP_LI << (32 - 2) | NTP_VN << (32 - 5) | NTP_MODE << (32 - 8)

# difference between NTP and system time (1900 to 1970 in seconds)
NTP_DELTA = 2208988800
# system_time = ntp_time - NTP_DELTA
# ntp_time = system_time + NTP_DELTA

def _to_frac(timestamp, bits=32):
    return int(abs(timestamp - int(timestamp)) * 2**bits)

def start_ntp_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((NTP_SERVER, NTP_PORT))

    # socket_timeout = 5.0
    # sock.settimeout(socket_timeout)

    print(f"NTP server listening on {NTP_SERVER}:{NTP_PORT} ...")
    while True:
        #### receive packet and record time
        try:
            ntp_packet, addr = sock.recvfrom(NTP_PACKET_SIZE)
        except:
            continue

        receive_time = time.time() + NTP_DELTA        
        unpacked_data = struct.unpack(NTP_PACKET_FORMAT, ntp_packet)
        origin_time = unpacked_data[10] + float(unpacked_data[11]) / 2**32
        transmit_time = time.time() + NTP_DELTA

        response_packet = struct.pack(NTP_PACKET_FORMAT, 
                        NTP_LI_VN_MODE, 0x00, 0x00, 0x00, 
                        0x00, 0x00, # reference time
                        int(origin_time), _to_frac(origin_time), # origin time
                        int(receive_time), _to_frac(receive_time), # receive time
                        int(transmit_time), _to_frac(transmit_time)) # transmit time

        sock.sendto(response_packet, addr)

        print(f"response sent to {addr[0]}:{addr[1]}")

    sock.close()
    print(f"NTP server shutdown on {NTP_SERVER}:{NTP_PORT} ...")


if __name__ == '__main__':
    start_ntp_server()


"""
reference timestamp index   = 4 and 5
origin timestamp index      = 6 and 7
receive timestamp index     = 8 and 9
transmit timestamp index    = 10 and 11
"""

