# NDS_Host_Advert_Prototype

My first attempt at emulating the host-side behavior of a Nintendo DS.

The Python script reads from the "filtered_beacons" and "reference_pcap" capture files, which were captured from an unmodded DS. The script then sets up two threads:

### Thread 1: 
Waits a constant interval, then writes the current state of a Scapy frame object and writes it to a pcap. This is a safer and non-hardware dependant way of testing what bytes we would actually be transmitting

### Thread 2:
Idles until Thread 1 transmits, at which point it modifies the contents of the frame object referred to by Thread 1 to hold the approrpriate information for the next frame (updated DTIM map, beacon timestamp, vendor-specific information which loops between ten different byestreams, etc). No locks need to be implemented as, like real Nintendo DS hardware, the frames are only "transmitted" (written to a file) every ~200ms, which is more than enough time for this thread to edit the object and avoid any concurrency issues.

I use a modified version of this script that actually transmits - such a program makes it easier to test client-side scripts that need to identify and respond to host transmissions.

For more information, check out the following link on how the Nintendo DS's Wifi behavior:

https://retroisle.com/others/nintendods/Technical/Firmware/wireless.php
