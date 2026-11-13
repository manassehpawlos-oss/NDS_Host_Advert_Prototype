import scapy.all as sc
import time
import threading
import copy
import sys

#Observed beacon_interval values from 0.222 to 0.213

# This program uses an existing pcap capture to generate its own frames for transmission.
# We first model an initial frame for transmission, then continiously modify that frame
# for subsequent transmissions. For this repo, we instead just write the files to a pcap.

# -------End the program by pressing enter! Otherwise, no files will be written.------

still_running = True  #super hackey, but otherwise daemon threads don't exit
count_to_read = 30 #too small = bad, bigger has no effect on program.
log_freq_multiplier = 1 #speeds up the otherwise accurate "tranmission" periods

source_pcap_file = "filtered_beacons.pcap"
output_pcap_file = "current.pcap"
reference_pcap_file = "reference.pcap"

def instance_starter(initial_packet,payload):
    seqnum_list = [0] #really just a non-mutable form of the seqnum.
    frame_list = [] #we log to and eventually return this list.
    beacon_interval = initial_packet[sc.Dot11Beacon].beacon_interval*1.024
    Tx_Radiotap = sc.RadioTap(bytes.fromhex("000014000e8a000002046c09a000000000003800"))
    
    threading.Thread(
        target=transmit_loop,
        daemon = True,
        args=(seqnum_list,
              beacon_interval,
              initial_packet,
              frame_list)
        ).start()
    
    threading.Thread(
        target = frame_updater,
        daemon = True,
        args=(seqnum_list,
              beacon_interval,
              initial_packet,
              payload)
        ).start()

    input("Press enter to quit and save frames.")
    return frame_list

def transmit_loop(seqnum_list,beacon_int,frame,outputted_frames):
    while still_running is True:
        time.sleep(beacon_int/(1000*log_freq_multiplier))
        print("logging frame")
        outputted_frames.append(copy.deepcopy(frame)) #copy to prevent mutable.
        seqnum_list[0] += 1

def frame_updater(seqnum_list,beacon_int, frame, payload):
    state = seqnum_list[0]-1
    while still_running is True:
        if state == seqnum_list[0]-1:
            print("Gotta update")
            state += 1
            frame[sc.Dot11].SC += 16 #seqnum updated
            frame[sc.Dot11Beacon].timestamp += int(beacon_int*10**6) #timestamp updated
            frame[sc.Dot11EltRates].channel = 1 #channel. Should synch with RT header
            frame[sc.Dot11EltRates][1].info = (
                bytes([(frame[sc.Dot11Elt][1].info[0]+1)%2,2,0,0,0]))#DTIM field updated
            frame[sc.Dot11EltVendorSpecific].info = (
                payload[seqnum_list[0]%10][sc.Dot11EltVendorSpecific].info[3:])
            #Fetches the next appropriate sequence number.


Tx_Radiotap = sc.RadioTap(bytes.fromhex("000014000e8a000002046c09a000000000003800"))
packet_list = sc.rdpcap(f"./{source_pcap_file}", count=count_to_read)

payload_list=[]
for i in range(10):
    payload_list.append(packet_list[4+i])
    #luckily, packets 4 to 14 of our source contain the ten frames that we want.
print(len(payload_list))

sample_packet=packet_list[0] 
noRT_noFCS = sc.Dot11(sc.raw(sample_packet)[sample_packet.len:-4]) #RT header and FCS sliced off
final_packet = Tx_Radiotap/copy.deepcopy(noRT_noFCS) #attached desired Tx header to frame
sc.wrpcap(f'./{reference_pcap_file}', [final_packet]) #log frame for troubleshooting

frame_list = instance_starter(final_packet,payload_list) #Now we enter our loop
sc.wrpcap('./{output_pcap_file}', frame_list) #and when we exit the loop, we write the list

still_running = False #daemon thread not exiting as expected. Jank fix to overcome this





