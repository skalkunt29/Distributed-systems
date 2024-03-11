import socket
import struct
import time
import csv

# NTP_SERVER = '127.0.0.1'
# NTP_PORT = 5000

NTP_SERVER = "pool.ntp.org"
NTP_PORT = 123

NTP_PACKET_FORMAT = "!12I"
NTP_PACKET_SIZE = 48    # 12 * 4

NTP_LI = 0      # 2 bits
NTP_VN = 4      # 3 bits
NTP_MODE = 3    # 3 bits

NTP_LI_VN_MODE = NTP_LI << (32 - 2) | NTP_VN << (32 - 5) | NTP_MODE << (32 - 8)

# difference between NTP and system time (1900 to 1970 in seconds)
NTP_DELTA = 2208988800
# system_time = ntp_time - NTP_DELTA
# ntp_time = system_time + NTP_DELTA


BURST_INTERVAL = 4 * 60     # in secs
TOTAL_TIME = 61 * 60        # in secs


def _to_frac(timestamp, bits=32):
    return int(abs(timestamp - int(timestamp)) * 2**bits)

def get_ntp_stats():
    # print('{:032b}'.format(NTP_LI_VN_MODE))
    
    delay_list = []
    offset_list = []

    t1 = []
    t2 = []
    t3 = []
    t4 = []


    total_num_packets = 8

    round_off_precision = 6
    socket_timeout = 1.0

    max_time = 60 * 2
    last_cutoff_time = 60 * 2
    
    # t_end is max_time from current time
    start_time = time.time()
    max_time_end = time.time() + max_time

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    addr = (NTP_SERVER, NTP_PORT)
    sock.settimeout(socket_timeout)

    num_packets = 0

    # while loop for max_time or until all packets received
    while time.time() < max_time_end and num_packets < total_num_packets:
        
        #### send a packet
        transmit_time = time.time() + NTP_DELTA
        ntp_packet = struct.pack(NTP_PACKET_FORMAT, 
                                NTP_LI_VN_MODE, 0x00, 0x00, 0x00, 
                                0x00, 0x00, # reference time
                                0x00, 0x00, # origin time
                                0x00, 0x00, # receive time
                                int(transmit_time), _to_frac(transmit_time)) # transmit time
        sock.sendto(ntp_packet, addr)


        #### receive packet and record time
        try:
            response_packet, addr = sock.recvfrom(NTP_PACKET_SIZE)
        except:
            continue

        dest_time = time.time() + NTP_DELTA
        unpacked_data = struct.unpack(NTP_PACKET_FORMAT, response_packet)

        origin_time = unpacked_data[6] + float(unpacked_data[7]) / 2**32

        # skip this packet if origin time is too old
        if origin_time < time.time() + NTP_DELTA - last_cutoff_time:
            print("skipping old packet")
            continue

        receive_time = unpacked_data[8] + float(unpacked_data[9]) / 2**32
        transmit_time = unpacked_data[10] + float(unpacked_data[11]) / 2**32

        delay_list.append(round((dest_time - origin_time) - (transmit_time - receive_time), round_off_precision))
        offset_list.append(round(((receive_time - origin_time) + (transmit_time - dest_time)) / 2, round_off_precision))

        t1.append(origin_time)
        t2.append(receive_time)
        t3.append(transmit_time)
        t4.append(dest_time)

        num_packets += 1

    sock.close()

    elapsed_time = round(time.time() - start_time, round_off_precision)
    print("time taken for this burst:", elapsed_time)
    
    return delay_list, offset_list, t1, t2, t3, t4



def save_to_csv(filename, row, mode='a'):
    # write the delay and offset values to the CSV file
    with open(filename, mode=mode, newline='') as file:
        writer = csv.writer(file)
        writer.writerow(row)



def ntp_client():        

    filename = "ntp_stats.csv"
    save_to_csv(filename, ['burst_num', 'i', 'burst_pairs', 
                           'offsets', 'delays', 'min_offset', 'min_delay',
                           'T1', 'T2', 'T3', 'T4'])

    burst_num = 0
    t_end = time.time() + TOTAL_TIME
    last_run_time = time.time() - BURST_INTERVAL
    
    while time.time() < t_end:
        if time.time() - last_run_time >= BURST_INTERVAL:
            last_run_time = time.time()
            print(burst_num, " ", end='')
            delay_list, offset_list, t1, t2, t3, t4 = get_ntp_stats()
            min_idx = delay_list.index(min(delay_list))
            for i in range(len(delay_list)):
                save_to_csv(filename, [burst_num, i, burst_num * 10 + i, 
                                       offset_list[i], delay_list[i], offset_list[min_idx], delay_list[min_idx],
                                        t1[i], t2[i], t3[i], t4[i]
                                       ])
            burst_num += 1


if __name__ == '__main__':
    #test the function
    ntp_client()
    



"""
reference timestamp index   = 4 and 5
origin timestamp index      = 6 and 7
receive timestamp index     = 8 and 9
transmit timestamp index    = 10 and 11
"""









