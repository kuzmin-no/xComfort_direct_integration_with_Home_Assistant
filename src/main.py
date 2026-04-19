import cc1101
import xComfort.rf_packet
import xComfort.device
import xComfort.mqtt as mqtt

Engineering_Tool_SN = 0x00000080

devices = {
    1: {
            "serial_number": 2159793,
            "device_name": "xComfort dimming actuator",
            "device_type": "dimmer",
            "object": None
    },
    2: {
            "serial_number": 4390086,
            "device_name": "xComfort switch actuator",
            "device_type": "switch",
            "object": None
    }
} 

try:
    import asyncio
except ImportError:
    import uasyncio as asyncio

async def main():
        await asyncio.sleep(0.01)

def get_actuator_state(serial_number):
    packet = xComfort.rf_packet.req_status(Engineering_Tool_SN, serial_number)
    for _ in range(3):
        result = transceiver.cc1101_send_with_ack(packet, padding=0x09)
        if (result != None) and (len(result) > 20):
            return result[19]
    return None

def get_deviceid_by_serial(serial_number):
    for id, device in devices.items():
        if device["serial_number"] == serial_number:
            return id
    return None


transceiver = cc1101.cc1101()
transceiver._debug = False

# Fill in information for MQTT auto discovery, and create entities
for id, device in devices.items():
    serial_number = device["serial_number"]

    if device["device_type"] == "switch":
        result = get_actuator_state(serial_number)
        pow_status = False
        if result != None:
            pow_status = result == 0x03
            print(f"Switching actuator -> pow_status: {pow_status}")
        devices[id]["object"] = mqtt.HaMqttSwitch(name=f"xcomfort_{serial_number}", full_name=device["device_name"], 
                                                  switch=xComfort.device.SwitchingActuator(transceiver, serial_number), pow_status=pow_status)


    if device["device_type"] == "dimmer":
        result = get_actuator_state(serial_number)
        pow_status = False
        dim_status = 0x00
        if result != None:
            pow_status = not (result == 0x00)
            dim_status = result
            print(f"Dimming actuator -> pow_status: {pow_status}, dim_status: {dim_status}")
        devices[id]["object"] = mqtt.HaMqttBrightnessLight(name=f"xcomfort_{serial_number}", full_name=device["device_name"], 
                                                           light=xComfort.device.DimmingActuator(transceiver, serial_number),
                                                           pow_status=pow_status, dim_status=dim_status)

try:
    while True:
        asyncio.run(main())
        # Sniff messages, check if there is something in RX FIFO
        if transceiver.cc1101_check_rxfifo():
            # try to get a data from RX FIFO
            packet = transceiver.cc1101_receive(flush_fifo=False, use_strobe=False, timeout=0)
            if packet:
                # Check if there is known message types in the packet, and extract destination serial number
                serial_number, pow_status = xComfort.rf_packet.check_packet_event(packet)
                if serial_number:
                    # Find device in the devices dictionary
                    id = get_deviceid_by_serial(serial_number)
                    if id:
                        # Get device type
                        device_type = devices[id]["device_type"]

                        if device_type == "switch":
                            devices[id]["object"].update(pow_status)
                            print(f"Switching actuator -> pow_status: {pow_status}")

                        if device_type == "dimmer":
                            # Need to request current brightnes from the dimmer
                            result = get_actuator_state(serial_number)
                            if result != None:
                                pow_status = not (result == 0x00)
                                dim_status = result
                                print(f"Dimming actuator -> pow_status: {pow_status}, dim_status: {dim_status}")
                                devices[id]["object"].update(pow_status, dim_status)

finally:
    mqtt.close_client()