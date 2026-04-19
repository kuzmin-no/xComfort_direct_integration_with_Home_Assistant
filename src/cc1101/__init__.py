from machine import Pin, SPI
import time

IOCFG2_REGISTER = 0x00
IOCFG0_REGISTER = 0x02
FIFOTHR_REGISTER = 0x03
SYNC1_REGISTER = 0x04
SYNC0_REGISTER = 0x05
PKTLEN_REGISTER = 0x06
PKTCTRL1_REGISTER =0x07
PKTCTRL0_REGISTER =0x08
FSCTRL1_REGISTER = 0x0B
FSCTRL0_REGISTER = 0x0C
FREQ2_REGISTER = 0x0D
FREQ1_REGISTER = 0x0E
FREQ0_REGISTER = 0x0F
MDMCFG4_REGISTER = 0x10
MDMCFG3_REGISTER = 0x11
MDMCFG2_REGISTER = 0x12
MDMCFG1_REGISTER = 0x13
MDMCFG0_REGISTER = 0x14
DEVIATN_REGISTER = 0x15
MCSM1_REGISTER = 0x17
MCSM0_REGISTER = 0x18
FOCCFG_REGISTER = 0x19
BSCFG_REGISTER = 0x1A
AGCCTRL2_REGISTER =0x1B
AGCCTRL1_REGISTER =0x1C
AGCCTRL0_REGISTER =0x1D
FREND1_REGISTER = 0x21
FREND0_REGISTER = 0x22
FSCAL3_REGISTER = 0x23
FSCAL2_REGISTER = 0x24
FSCAL1_REGISTER = 0x25
FSCAL0_REGISTER = 0x26
PATABLE_REGISTER = 0x3E
MARCSTATE_REGISTER = 0x35

STROBE_SRES = 0x30  # Reset chip
STROBE_SRX = 0x34   # Enable RX
STROBE_STX = 0x35   # Enable TX
STROBE_SIDLE = 0x36 # Exit RX / TX, turn off frequency synthesizer
STROBE_SFRX = 0x3A  # Flush RX FIFO
STROBE_SFTX = 0x3B  # Flush TX FIFO

READ_BYTE = 0x80
READ_BURST = 0xC0
WRITE_BYTE = 0x00
WRITE_BURST = 0x40

PARTNUM = 0x30 | READ_BURST
VERSION = 0x31 | READ_BURST
TXBYTES = 0x3A | READ_BURST
RXBYTES = 0x3B | READ_BURST
TX_FIFO = 0x3F | WRITE_BYTE
TX_FIFO_BURST = 0x3F | WRITE_BURST
RX_FIFO = 0x3F | READ_BYTE
RX_FIFO_BURST = 0x3F | READ_BURST

class cc1101:
    def __init__(self, csn_pin=Pin(8, Pin.OUT, value=1), sck_pin=Pin(6), mosi_pin=Pin(7), miso_pin=Pin(4), gdo0_pin=Pin(9, Pin.IN), gdo2_pin=Pin(10, Pin.IN)):
        self.gdo0_pin = gdo0_pin
        self.gdo2_pin = gdo2_pin
        self.csn_pin = csn_pin
        self._debug = True

        self.spi = SPI(0,
                baudrate=5000000,
                polarity=0,
                phase=0,
                sck=sck_pin,
                mosi=mosi_pin,
                miso=miso_pin)

        self.cc1101_init()
        partnum = self.cc1101_read_reg(PARTNUM)
        version = self.cc1101_read_reg(VERSION)
        if ((partnum == 0x00) and (version == 0x00)) or ((partnum == 0xFF) and (version == 0xFF)):
            raise RuntimeError("Transceiver CC1101 not found!")
        elif self._debug:
            print(f"Part number: {partnum}\nChip version: {version}")

    def reverse_bits_in_byte(self, n):
        """
        Reverses bits in a byte
        """
        result = 0
        for i in range(8): # Loop 8 times for a byte
            result = (result << 1) | (n & 1)
            n >>= 1
        return result

    def crc16_kermit_manual(self, data):
        """
        Calcualte CRC16 Kermit
        """
        crc = 0x0000
        poly = 0x8408

        for byte in data:
            crc ^= byte
            for _ in range(8):
                if crc & 0x0001:
                    crc = (crc >> 1) ^ poly
                else:
                    crc >>= 1
                crc &= 0xFFFF

        return crc

    def cc1101_write_reg(self, addr, value):
        self.csn_pin.value(0)
        self.spi.write(bytearray([addr, value]))
        self.csn_pin.value(1)

    def cc1101_read_reg(self, addr):
        self.csn_pin.value(0)
        self.spi.write(bytearray([addr | READ_BYTE]))
        val = self.spi.read(1)[0]
        self.csn_pin.value(1)
        return val

    def cc1101_strobe(self, cmd):
        self.csn_pin.value(0)
        self.spi.write(bytearray([cmd]))
        self.csn_pin.value(1)

    def cc1101_dump_registers(self):
        print("\n--- CC1101 REGISTER DUMP ---")
        for reg in range(0x00, 0x2F):  # Config registers
            val = self.cc1101_read_reg(reg)
            print("0x{:02X}: 0x{:02X}".format(reg, val))
        print("--- END OF CONFIG REGS ---\n")

        # Status registers (read with burst bit)
        status_regs = {
            PARTNUM: "PARTNUM",
            VERSION: "VERSION",
            0x32: "FREQEST",
            0x33: "LQI",
            0x34: "RSSI",
            0x35: "MARCSTATE",
            0x36: "WORTIME1",
            0x37: "WORTIME0",
            0x38: "PKTSTATUS",
            0x39: "VCO_VC_DAC",
            TXBYTES: "TXBYTES",
            RXBYTES: "RXBYTES",
        }

        print("--- STATUS REGISTERS ---")
        for reg, name in status_regs.items():
            val = self.cc1101_read_reg(reg | READ_BURST)
            print("{} (0x{:02X}): 0x{:02X}".format(name, reg, val))
        print("--- END OF STATUS REGS ---\n")

    def cc1101_init(self):
        # Reset chip
        self.cc1101_strobe(STROBE_SRES)
        time.sleep_ms(10)

        # Basic configuration for 868.3 MHz, 2-FSK, Manchester
        regs = {
            IOCFG2_REGISTER: 0x04,
            IOCFG0_REGISTER: 0x06,  # 0x06 -> sync word
            FIFOTHR_REGISTER: 0x07,
            SYNC1_REGISTER: 0xAA,
            SYNC0_REGISTER: 0xAB,
            PKTLEN_REGISTER: 0x32,
            PKTCTRL1_REGISTER: 0x00,
            PKTCTRL0_REGISTER: 0x00, # 0x00 -> Fifo mode
            FSCTRL1_REGISTER: 0x06,
            FSCTRL0_REGISTER: 0x00,
            FREQ2_REGISTER: 0x21,
            FREQ1_REGISTER: 0x66,
            FREQ0_REGISTER: 0x15,
            MDMCFG4_REGISTER: 0xA9,  # 0xx9 -> 19.2    0xxA -> 38.4   0xxB -> 76.8
            MDMCFG3_REGISTER: 0x83,
            MDMCFG2_REGISTER: 0x0A,  # (2-FSK + Manchester) -> 0x0A
            MDMCFG1_REGISTER: 0x02,
            MDMCFG0_REGISTER: 0xF8,
            DEVIATN_REGISTER: 0x42,  # 0x34 -> 20 kHz  0x42 -> 32 kHz   0x52 -> 64 kHz
            MCSM1_REGISTER: 0x3F,  # Switch to RX mode after TX
            MCSM0_REGISTER: 0x18,
            FOCCFG_REGISTER: 0x16,
            BSCFG_REGISTER: 0x6C,
            AGCCTRL2_REGISTER: 0x03,
            AGCCTRL1_REGISTER: 0x50,
            AGCCTRL0_REGISTER: 0x91,
            FREND1_REGISTER: 0x56,
            FREND0_REGISTER: 0x10,
            FSCAL3_REGISTER: 0xE9,
            FSCAL2_REGISTER: 0x2A,
            FSCAL1_REGISTER: 0x00,
            FSCAL0_REGISTER: 0x1F,
            PATABLE_REGISTER: 0xFF,
        }

        for reg, val in regs.items():
            self.cc1101_write_reg(reg, val)

        if self._debug:
            print("CC1101 initialized")

    def print_hex(self, data, title="Data"):
        print(f"{title}: ", end="")
        for item in data:
            print(f"{item:02x}", end=" ")
        print()

    def cc1101_send(self, out_data, wait=True, add_crc=True, padding=0x00):
        self.cc1101_strobe(STROBE_SIDLE)
        time.sleep_ms(1)
        self.cc1101_strobe(STROBE_SFTX)
        self.cc1101_strobe(STROBE_SFRX)

        raw_data = []
        for one_byte in out_data:
            raw_data.append(one_byte)

        if add_crc:
            calculated_crc = self.crc16_kermit_manual(out_data)
            raw_data.append(calculated_crc & 0xff)
            raw_data.append(calculated_crc >> 8)

        if self._debug:
            self.print_hex(raw_data, title="Sending")

        if padding > 0:
            for _ in range(padding):
                raw_data.append(0x00)

        packet_length = len(raw_data)
        self.cc1101_write_reg(PKTLEN_REGISTER, packet_length)

        data = []
        for one_byte in raw_data:
            data.append(self.reverse_bits_in_byte(one_byte ^ 0xff))

        # Write length + data
        self.csn_pin.value(0)
        self.spi.write(bytearray([TX_FIFO_BURST]))
        self.spi.write(bytearray(data))
        self.csn_pin.value(1)

        self.cc1101_strobe(STROBE_STX)

        if wait:
            # Wait for GDO0 to go high then low (packet sent)
            while not self.gdo0_pin.value():
                pass
            while self.gdo0_pin.value():
                pass

    def cc1101_check_rxfifo(self):
        return self.cc1101_read_reg(RXBYTES)

    def cc1101_receive(self, flush_fifo=True, use_strobe=True, timeout=500):
        if flush_fifo:
            self.cc1101_strobe(STROBE_SFRX)
        if use_strobe:
            self.cc1101_strobe(STROBE_SRX)

        start = time.time()
        while True:

            #print("Waiting for packet...")
            while not self.gdo0_pin.value():  # GDO0 goes high when packet received
                pass
            #print("Waiting for end of the packet...")
            while  self.gdo0_pin.value():
                pass

            # Read RX FIFO
            packet_length = self.cc1101_read_reg(RXBYTES)
            #print(f"Length: {packet_length:02x} ")
            if packet_length > 0:
                break

            if ((time.time() - start) * 1000) >= timeout:
                return None

        self.csn_pin.value(0)
        self.spi.write(bytes([RX_FIFO_BURST]))
        data = self.spi.read(packet_length)
        self.csn_pin.value(1)

        if packet_length > 10:
            calculated_packet_length = self.reverse_bits_in_byte(data[2] ^ 0xff)
            if packet_length >= calculated_packet_length:
                packet_length = calculated_packet_length
                result = []
                for one_byte in data:
                    result.append(self.reverse_bits_in_byte(one_byte ^ 0xff))
                    if calculated_packet_length == 1:
                        break
                    else:
                        calculated_packet_length -= 1

                calculated_crc = self.crc16_kermit_manual(result[:packet_length - 2])
                crc = (result[packet_length - 1] << 8) | result[packet_length - 2]
                #print(f"{calculated_crc:04X}, {crc:04X}")
                if calculated_crc == crc:
                    if self._debug:
                        self.print_hex(result[:packet_length], title="Receive")
                    #crc_check = calculated_crc == crc
                    #print(f"\t -> CRC: {crc_check}")
                    return result[:packet_length]
        return None

    def cc1101_send_with_ack(self, out_data, padding=0x00):
        self.cc1101_send(out_data, wait=False, add_crc=False, padding=padding)
        return self.cc1101_receive(flush_fifo=False, use_strobe=False)