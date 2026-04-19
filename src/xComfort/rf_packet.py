Message_Type_dict = {

    0x50: "MSG_ON",
    0x51: "MSG_OFF",
    0x11: "MSG_ALLIVE",
    0x52: "MSG_SWITCH_ON",
    0x53: "MSG_SWITCH_OFF",
    0x54: "MSG_UP_PRESSED",
    0x55: "MSG_UP_RELEASED",
    0x56: "MSG_DOWN_PRESSED",
    0x57: "MSG_DOWN_RELEASED",
    0x59: "MSG_PWM",
    0x5a: "MSG_FORCED",
    0x5b: "MSG_SINGLE_ON",
    0x5c: "MSG_CHECKLOAD",
    0x61: "MSG_TOGGLE",
    0x62: "MSG_VALUE",
    0x63: "MSG_ZU_KALT",
    0x64: "MSG_ZU_WARM",
    0x70: "MSG_STATUS",
    0x72: "MSG_STATUS_REQ_APPL",
    0x71: "MSG_STATUS_APPL",
    0x30: "MSG_GET_EEPROM",
    0x31: "MSG_SET_EEPROM",
    0x09: "MSG_STAY_ONLINE",
    0x18: "MSG_GET_OFFLINE",
    0x37: "MSG_TIME",
    0x38: "MSG_DATE",
    0x39: "MSG_PAKET",
    0x01: "MSG_ACK",
    0x43: "MSG_KILL",
    0x44: "MSG_FACTORY",
    0x32: "MSG_GET_CRC",
    0x0a: "MSG_SET_TARGET",
    0x12: "MSG_ASK_FOR_RSSI",
    0x13: "MSG_UNKNOWN1"

}

Telegramm_Type_dict = {
    0: "Not defined",
    1: "Direct, without routing",
    2: "Acknowledge",
    3: "Routed"
}

Telegramm_Klasse1_dict = {
    0x01: "Request",
    0x02: "Confirm",
    0x08: "Applications EndToEnd",
    0x10: "Resend",
}

Telegramm_Klasse2_dict = {
    0x00: "User Event",
    0x20: "Cyclical message",
    0x60: "Home-Manager",
    0x80: "Engineering Tool",
    0xA0: "Answer"
}

Batterie_Status_dict = {
    0x00: "Learning",
    0x01: "Weak",
    0x02: "Medium",
    0x03: "Almost full",
    0x04: "Full",
    0x07: "Mains powered"
}

Data_type_dict = {
    0x0: "NO_TELEGRAM_DATA",
    0x1: "PROZENT",
    0x2: "DATA_TYPE_UCHAR",
    0x3: "SSHORT_1KOMMA",
    0xd: "USHORT_NO_KOMMA",
    0x17: "RC_DATEN",
    0x7: "MEMORY_REQ",
    0x6: "MEMORY",
    0x1b: "MEMORY32_RE",
    0x1a: "MEMORY32",
    0xc: "ALLIVE_FILTER",
    0x4: "ANSI_FLOAT",
    0x1e: "DATA_TYPE_TIME",
    0x1f: "DATA_TYPE_DATE",
    0x20: "DATA_TYPE_PAKET",
    0x25: "DATA_TYPE_UNSIGNED_LONG",
    0x26: "DATA_TYPE_ULONG_1KOMMA",
    0x27: "DATA_TYPE_ULONG_2KOMMA",
    0x28: "DATA_TYPE_ULONG_3KOMMA",
    0x29: "USHORT_1KOMMA",
    0x2a: "USHORT_2KOMMA",
    0x2b: "USHORT_3KOMMA",
    0x2d: "DIMPLEX_DATEN",
    0xf0: "ARRAY",
    0x2e: "DATA_TYPE_SLONG_NO_KOMMA",
    0x2f: "DATA_TYPE_SLONG_1KOMMA",
    0x30: "DATA_TYPE_SLONG_2KOMMA",
    0x31: "DATA_TYPE_SLONG_3KOMMA",
    0x32: "DATA_TYPE_SSHORT_NO_KOMMA",
    0x33: "DATA_TYPE_SSHORT_2KOMMA",
    0x34: "DATA_TYPE_SSHORT_3KOMMA",
    0xa: "SERIALNUMBER",
    0x39: "DATA_TYPE_STATUS",
    0x3a: "DATA_TYPE_STATUS_REQ",
    0x3f: "DATA_TYPE_RCF55_OUT",
    0x40: "DATA_TYPE_RCF55_IN",
    0x41: "DATA_TYPE_RCF55_SETPOINTS",
    0x42: "DATA_TYPE_RCF55_REQ"
}

def print_hex(data, title="Data"):
    print(f"{title}: ", end="")
    for item in data:
        print(f"{item:02x}", end=" ")
    print()

def crc16_kermit_manual(data):
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

def get_key_by_value(my_dict, search_value):
    return next((k for k, v in my_dict.items() if v == search_value), None)

def decode_packet(data):
    """
    Decode packet in humar readable representation
    """
    if data == None:
        print("Nothing to decode.")
        return
    
    Message_Type = data[0]
    print("\tMessage_Type:", Message_Type_dict[Message_Type])

    Message_Length = data[2]
    print("\tMessage_Length:", Message_Length)

    Telegramm_Type = (data[3] & 0xF0) >> 4
    print("\tTelegramm_Type:", Telegramm_Type_dict[Telegramm_Type])

    Telegramm_Number = data[3] & 0x0F
    print("\tTelegramm_Number:", Telegramm_Number)

    Telegramm_Klasse1 = data[4]
    Telegramm_Klasse_result = ""
    for key, value in Telegramm_Klasse1_dict.items():
        if (Telegramm_Klasse1 & key) > 0:
            Telegramm_Klasse_result += value + " | "
    Telegramm_Klasse2 = data[4] & 0xF0
    Telegramm_Klasse_result += Telegramm_Klasse2_dict[Telegramm_Klasse2]
    print("\tType:", Telegramm_Klasse_result)

    Batterie_Status = data[5] & 0x07
    print("\tBatterie_Status:", Batterie_Status_dict[Batterie_Status])

    Source_channel = data[6]
    print("\tSource_channel:", Source_channel)

    Source_serialnumber = int.from_bytes(bytes(data[7:11]), 'little')
    print("\tSource_serialnumber:", Source_serialnumber)

    Destination_channel = data[11]
    print("\tDestination_channel:", Destination_channel)

    Destination_serialnumber = int.from_bytes(bytes(data[12:16]), 'little')
    print("\tDestination_serialnumber:", Destination_serialnumber)

    if len(data) > 18:
        Data_type = data[16]
        print("\tData_type:", Data_type_dict[Data_type])

        if Data_type == 0x06:
            Data_address = int.from_bytes(bytes(data[18:20]), 'little')
            print(f"\tData_address: 0x{Data_address:04X}")
            Data_length = data[20]
            print("\tData_length:", Data_length)
            print("\tData: ", end="")
            for i in range(21, 21 + Data_length):
                print("{:02X}".format(data[i]), end=" ")
            print()

    crc16 = int.from_bytes(bytes(data[-2:]), 'little')
    print(f"\tCRC: {crc16:04X}")

    print()

def check_packet_event(data):
    """
    Check for known message types and extract serial number
    """
    Destination_serialnumber = int.from_bytes(bytes(data[12:16]), 'little')
    Message_Type = data[0]
    message = Message_Type_dict[Message_Type]
    if (message == "MSG_ON") or (message == "MSG_UP_RELEASED") or (message == "MSG_DOWN_RELEASED"):
        return Destination_serialnumber, True
    elif message ==  "MSG_OFF":
        return Destination_serialnumber, False
    else:
        return None, None

def create_packet_from_json(packet):
    """
    Create RF packet from json representation
    """
    result_packet = []
    result_packet.append(packet["Message_Type"])
    result_packet.append(0x00) # Unknown
    result_packet.append(0x00) # Packet length
    result_packet.append(packet["Telegramm_Type"] << 4 | packet["Telegramm_Number"])
    result_packet.append(packet["Type"])
    result_packet.append(packet["Batterie_Status"])
    result_packet.append(packet["Source_channel"])
    for one_byte in packet["Source_serialnumber"].to_bytes(4, 'little'):
        result_packet.append(one_byte)
    result_packet.append(packet["Destination_channel"])
    for one_byte in packet["Destination_serialnumber"].to_bytes(4, 'little'):
        result_packet.append(one_byte)

    Data_type = packet["Data_type"]
    result_packet.append(packet["Data_type"])
    if Data_type == 0x07: # MEMORY_REQ
        result_packet.append(0x00)
        for one_byte in packet["Data_address"].to_bytes(2, 'little'):
            result_packet.append(one_byte)
        result_packet.append(packet["Data_length"])
    if Data_type in [0x0c, 0x01]: # ALLIVE_FILTER, MSG_FORCED
        result_packet.append(0x00)
        result_packet.append(packet["Data"])
    # Calcualte packet length
    result_packet[2] = len(result_packet) + 2
    # Add crc16
    for one_byte in crc16_kermit_manual(result_packet).to_bytes(2, 'little'):
        result_packet.append(one_byte)
    return bytearray(result_packet)

def req_status(src_serialnumber, dst_serialnumber):

    packet = {
        "Message_Type": get_key_by_value(Message_Type_dict, "MSG_STATUS"),
        "Telegramm_Type": 1, # Direct
        "Telegramm_Number": 0,
        "Type": 0x81, # Request | Engineering Tool
        "Batterie_Status": 0x07, # Mains powered
        "Source_channel": 0,
        "Source_serialnumber": src_serialnumber,
        "Destination_channel": 0,
        "Destination_serialnumber": dst_serialnumber,
        "Data_type": get_key_by_value(Data_type_dict, "NO_TELEGRAM_DATA")
    }
    return create_packet_from_json(packet)

def set_brightness(src_serialnumber, dst_serialnumber, value):

    packet = {
        "Message_Type": get_key_by_value(Message_Type_dict, "MSG_FORCED"),
        "Telegramm_Type": 1, # Direct
        "Telegramm_Number": 0,
        "Type": 0x82, # Confirm | Engineering Tool
        "Batterie_Status": 0x07, # Mains powered
        "Source_channel": 0,
        "Source_serialnumber": src_serialnumber,
        "Destination_channel": 0,
        "Destination_serialnumber": dst_serialnumber,
        "Data_type": get_key_by_value(Data_type_dict, "PROZENT"),
        "Data": value
    }
    return create_packet_from_json(packet)

def switch_on(src_serialnumber, dst_serialnumber):

    packet = {
        "Message_Type": get_key_by_value(Message_Type_dict, "MSG_ON"),
        "Telegramm_Type": 1, # Direct
        "Telegramm_Number": 0,
        "Type": 0x82, # Confirm | Engineering Tool
        "Batterie_Status": 0x07, # Mains powered
        "Source_channel": 0,
        "Source_serialnumber": src_serialnumber,
        "Destination_channel": 0,
        "Destination_serialnumber": dst_serialnumber,
        "Data_type": get_key_by_value(Data_type_dict, "NO_TELEGRAM_DATA")
    }
    return create_packet_from_json(packet)

def switch_off(src_serialnumber, dst_serialnumber):

    packet = {
        "Message_Type": get_key_by_value(Message_Type_dict, "MSG_OFF"),
        "Telegramm_Type": 1, # Direct
        "Telegramm_Number": 0,
        "Type": 0x82, # Confirm | Engineering Tool
        "Batterie_Status": 0x07, # Mains powered
        "Source_channel": 0,
        "Source_serialnumber": src_serialnumber,
        "Destination_channel": 0,
        "Destination_serialnumber": dst_serialnumber,
        "Data_type": get_key_by_value(Data_type_dict, "NO_TELEGRAM_DATA")
    }
    return create_packet_from_json(packet)

def get_eeprom(src_serialnumber, dst_serialnumber, start_from, length):

    packet = {
        "Message_Type": get_key_by_value(Message_Type_dict, "MSG_GET_EEPROM"),
        "Telegramm_Type": 1, # Direct
        "Telegramm_Number": 0,
        "Type": 0x81, # Request | Engineering Tool
        "Batterie_Status": 0x07, # Mains powered
        "Source_channel": 0,
        "Source_serialnumber": src_serialnumber,
        "Destination_channel": 0,
        "Destination_serialnumber": dst_serialnumber,
        "Data_type": get_key_by_value(Data_type_dict, "MEMORY_REQ"),
        "Data_address": start_from,
        "Data_length": length
    }
    return create_packet_from_json(packet)

def scan(src_serialnumber=0x00000080, dst_serialnumber=0x00000000, alive_filter=0x03):

    packet = {
        "Message_Type": get_key_by_value(Message_Type_dict, "MSG_ALLIVE"),
        "Telegramm_Type": 1, # Direct
        "Telegramm_Number": 0,
        "Type": 0x81, # Request | Engineering Tool
        "Batterie_Status": 0x07, # Mains powered
        "Source_channel": 0,
        "Source_serialnumber": src_serialnumber,
        "Destination_channel": 0,
        "Destination_serialnumber": dst_serialnumber,
        "Data_type": get_key_by_value(Data_type_dict, "ALLIVE_FILTER"),
        "Data": alive_filter
    }
    return create_packet_from_json(packet)