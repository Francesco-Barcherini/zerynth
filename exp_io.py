from ads7128 import *
from time import sleep
from random import random

"""
NOTE
In zerynth expansions the numbering of the screws do not match the pin number of ads7128
here is a map for each expansion to know who's who.

RELAY
OUT1 = 1
OUT2 = 7
OUT3 = 6
OUT4 = 0
OUT5 = 3
OUT6 = 2

IO
OUT1 = 4
OUT2 = 5
OUT3 = 2
OUT4 = 3
AIN1 = 0
AIN2 = 1
DIN1 = 6
DIN2 = 7

AIN
AIN1 = 0
AIN2 = 1
AIN3 = 2
AIN4 = 3
AIN5 = 7
AIN6 = 6
AIN7 = 5
AIN8 = 4
"""


def out_test(ads, pin):
    ads.pin_toggle(pin)
    print(f"SET OUT {pin} TO:", ads.pin_read_latch(pin))
    
def ain_test(ads, pin):
    raw_val = ads.adc_read(pin)
    #print(f"A {pin} INPUT: " + str(raw_val) + " -> " + str((raw_val-2048)/200), "")
    print(f"A {pin} INPUT: " + str(raw_val) + " -> " + str((raw_val-2048)/100), "")
    
def din_test(ads, pin):
    print(f"D {pin} INPUT:", ads.pin_read(pin))

def all_io(ads):
    out_test(ads, 4)
    out_test(ads, 5)
    out_test(ads, 2)
    out_test(ads, 3)

    ain_test(ads, 0)
    ain_test(ads, 1)

    din_test(ads, 6)
    din_test(ads, 7)



ads_io = ADS7128(addr=0x10)
ads_io._gpo_pp(4) #OUT1

ads_relay = ADS7128(addr=0x11)
ads_relay._gpo_pp(1) #OUT2

value = 1
while True:
    ads_io.pin_write(4,value)
    ads_relay.pin_write(1,1-value)

    value = 0 if random() < 0.75 else 1
    sleep(0.1)

'''
if __name__ == '__main__':
    # Init ads7128 device
    ads = ADS7128(7, 0x10)
    # Enable pins as output, input and analog
    ads._gpo_pp(4) #OUT1
    ads._gpo_pp(5) #OUT2
    ads._gpo_pp(2) #OUT3
    ads._gpo_pp(3) #OUT4
    ads._analog(0) #AIN1
    ads._set_osr(4)
    ads._analog(1) #AIN2
    ads._set_osr(4)
    ads._gpi(6) #DIN1
    ads._gpi(7) #DIN2



    write_value = 1
    count = 0

    start = time.time()
    while count < 10000:
        #ads.print_registers()
        # out_test(ads, 4)
        ain_test(ads, 0)
        # din_test(ads, 6)
        #out_test(ads) if random() < 0.5 else din_test(ads)

        #all_io(ads)
        count+=1
        
    seconds = time.time() - start
    count *= 12
    freq = count/seconds
    print(f"{count} op in {seconds} seconds ==> freq = {freq}Hz")
'''
