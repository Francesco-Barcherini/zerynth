from smbus2 import SMBus, i2c_msg
import time
from enum import Enum

ADS_REG_READ =    0b00010000
ADS_REG_WRITE =   0b00001000
ADS_SET_BIT =     0b00011000
ADS_CLEAR_BIT =   0b00100000
ADS_BLOCK_READ =  0b00110000
ADS_BLOCK_WRITE = 0b00101000

REG_SYS_STATUS =    0x00
REG_GENERAL_CFG =   0x01
REG_OSR_CFG =       0x03
REG_PIN_CFG =       0x05
REG_GPIO_CFG=       0x07
REG_GPO_DRIVE_CFG = 0x09
REG_GPO_VAL =       0x0B
REG_GPI_VAL =       0x0D
REG_CH_SEL =        0x11


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

class ADS7128():
    def __init__(self, nbus=7, addr=0x10):
        # nbus: number of i2c bus to use
        # addr: is 0x10 + value_of_the_addr_selector (0x10 -> 0x13)
        self.bus = SMBus(nbus)
        self.addr = addr

    def i2c_transmit(self, tx, rx_size):
        msgw = i2c_msg.write(self.addr, tx)
        msgr = i2c_msg.read(self.addr, rx_size)

        if rx_size:
            self.bus.i2c_rdwr(msgw, msgr)
            return list(msgr)
        else:
            self.bus.i2c_rdwr(msgw)
            return None

    def bit_set(self, reg, val):
        return self.i2c_transmit([ADS_SET_BIT, reg, val], 0)

    def bit_clear(self, reg, val):
        return self.i2c_transmit([ADS_CLEAR_BIT, reg, val], 0)

    def reg_write(self, reg, val):
        return self.i2c_transmit([ADS_REG_WRITE, reg, val], 0)

    def reg_read(self, reg):
        return self.i2c_transmit([ADS_REG_READ, reg], 1)[0]

    def block_write(self, reg, buff):
        b = [ADS_BLOCK_WRITE, reg]
        b.append(buff)
        return self.i2c_transmit(b, 0) 

    def block_read(self, size):
        return self.i2c_transmit([ADS_BLOCK_READ], size)

    def reset(self):
        # Reset ADS7128
        self.bit_set(REG_GENERAL_CFG, 1)
        time.sleep(0.05)
        for i in range(5):
            try:
                r1 = self.reg_read(REG_SYS_STATUS)
                r2 = self.reg_read(REG_GENERAL_CFG)
                if (r1&1) == 1 and (r2&1) == 0:
                    break
            except:
                pass
            time.sleep(0.01)
        else:
            print("Reset Error")
            return 1
        self.bit_set(REG_SYS_STATUS, 1)
        time.sleep(0.05)
        for i in range(10):
            try:
                r1 = self.reg_read(REG_SYS_STATUS)
                if (r1&1) == 0:
                    return 0
            except:
                pass
            time.sleep(0.01)
        else:
            print("Reset Error")
            return 1

    def _pin_to_bit(self, pin):
        return 1 << pin

    def _gpo_pp(self, pin):
        # Configure selected pin as OUTPUT PUSHPULL
        bit = self._pin_to_bit(pin)
        self.bit_set(REG_PIN_CFG, bit)
        self.bit_set(REG_GPIO_CFG, bit)
        self.bit_set(REG_GPO_DRIVE_CFG, bit)

    def _gpo_od(self, pin):
        # Configure selected pin as OUTPUT OPENDRAIN
        bit = self._pin_to_bit(pin)
        self.bit_set(REG_PIN_CFG, bit)
        self.bit_set(REG_GPIO_CFG, bit)
        self.bit_clear(REG_GPO_DRIVE_CFG, bit)

    def _gpi(self, pin):
        # Configure selected pin as INPUT (NOPULL)
        bit = self._pin_to_bit(pin)
        self.bit_set(REG_PIN_CFG, bit)
        self.bit_clear(REG_GPIO_CFG, bit)

    def _analog(self, pin):
        # Configure selected pin as ANALOG, requires _set_osr to be call after
        bit = self._pin_to_bit(pin)
        self.bit_clear(REG_PIN_CFG, bit)

    def pin_write(self, pin, val):
        # Write pin value
        bit = self._pin_to_bit(pin)
        if not val:
            self.bit_clear(REG_GPO_VAL, bit)
        else:
            self.bit_set(REG_GPO_VAL, bit)

    def pin_read_latch(self, pin):
        # Read value set of an Output pin
        v = self.reg_read(REG_GPO_VAL)
        return (v >> pin)&1 

    def pin_read(self, pin):
        # Read input pin
        v = self.reg_read(REG_GPI_VAL)
        return (v >> pin)&1
    
    def pin_toggle(self, pin):
        ret = self.pin_read_latch(pin)
        if ret >= 0:
            self.pin_write(pin, 1 if ret==0 else 0)

    def _set_osr(self, osr):
        self.reg_write(REG_OSR_CFG, osr)

    def adc_read(self, pin, size=2):
        # Read analog channel
        # Format: [vvvvvvvv][vvvv0000]
        # Returns the 12bit value 
        self.reg_write(REG_CH_SEL, pin)
        blocks = self.block_read(size)
        return (blocks[0] << 4) + (blocks[1] >> 4)

if __name__ == '__main__':
    # Here is a NOT TESTED example

    # Init ads7128 device
    ads = ADS7128(7, 0x11)

    # Enable pins as output, input and analog
    pin = 1
    ads._gpo_pp(pin)
    #ads._gpi(1)
    #ads._analog(2)
    #ads._set_osr(2, 0)

    write_value = 1
    while True:
        ads.pin_write(pin, write_value)
        #write_value = 1 - write_value
        time.sleep(0.5)

    '''
    while True:
        ads.pin_write(0, write_value)
        # switch values since I did not implement toggle yet
        write_value = 1 - write_value
        print("SET OUT TO:", ads.pin_read_latch(0))

        print("D INPUT:", ads.pin_read(1))

        print("A INPUT:", ads.adc_read(2,2))

        time.sleep(1)
    '''


