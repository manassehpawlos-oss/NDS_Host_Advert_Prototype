# NDS_Host_Advert_Prototype

My first attempt at emulating the host-side behavior of a Nintendo DS.

The Python script reads from the "filtered_beacons" capture file, which were captured from an unmodded DS. The script then sets up two threads:

### Thread 1: 
Waits a constant interval, then refers to the same Scapy frame object and transmits that.

### Thread 2:
Idles until Thread 1 transmits, at which point it modifies the contents of the frame object referred to by Thread 1 to hold the approrpriate information for the next frame (updated DTIM map, beacon timestamp, vendor-specific information which loops between ten different bytes, etc). This thread only acts after Thread 1 is finished, and this thread normally has >=200ms to make the adjustments, so no locking is necessary.

I use a modified version of this script for actual testing - it's nice to be able to mock host transmissions on the same frequency you want, as opposed to switching frequencies to catch whichever one a legitimate Nintendo DS chose to do.

For more information, check out the following link on how the Nintendo DS's Wifi behavior:

https://retroisle.com/others/nintendods/Technical/Firmware/wireless.php
