import xComfort.rf_packet

class SwitchingActuator(object):
    def __init__(self, transceiver, serial_number):
        self.transceiver = transceiver
        self.serial_number = serial_number

    def on(self):
        print(f"Switching on {self.serial_number}")
        packet = xComfort.rf_packet.switch_on(0x00000080, self.serial_number)
        result = self.transceiver.cc1101_send_with_ack(packet)

    def off(self):
        print(f"Switching off {self.serial_number}")
        packet = xComfort.rf_packet.switch_off(0x00000080, self.serial_number)
        result = self.transceiver.cc1101_send_with_ack(packet)

class DimmingActuator(SwitchingActuator):
    def __init__(self, transceiver, serial_number):
        super().__init__(transceiver, serial_number)

    def brightness(self, value):
        print(f"Dimming to {value} of {self.serial_number}")
        packet = xComfort.rf_packet.set_brightness(0x00000080, self.serial_number, value)
        result = self.transceiver.cc1101_send_with_ack(packet)
