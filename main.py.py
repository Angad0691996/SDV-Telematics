#!/usr/bin/python
#mqtt sample code
# this program will subscribe and show all the messages sent by its companion
# subscribe.py using the AWS IoT hub

import paho.mqtt.client as paho
import os
import socket
import ssl
import json
import csv
from datetime import datetime
import serial
#import boto3

# Global variables to store received JSON messages
received_messages = []


# Function to send messages to a USB to serial adapter
def send_message_to_usb(message, serial_port):
    try:
        # Configure the serial port
        ser = serial.Serial(
            serial_port,  # port="/dev/ttyACM0",
            baudrate=115200,
            bytesize=serial.EIGHTBITS,  # 8 data bits
            parity=serial.PARITY_NONE,  # No parity
            stopbits=serial.STOPBITS_ONE,  # 1 stop bit
            timeout=None,  # No timeout (adjust as needed)
            xonxoff=False,  # No software flow control
            rtscts=False,  # No hardware flow control
        )

        # Send the message to the USB to serial adapter
        ser.write(message.encode())
        ser.write(b"\r")

        # Close the serial connection when done
        ser.close()
    except Exception as e:
        print(f"Error: {str(e)}")


def on_connect(client, userdata, flags, rc):
    print("Connection returned result: " + str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    # client.subscribe("#" , 1 )
    client.subscribe("carDoor/status", 1)
    #client.publish("carDoor/status",1)
    

def on_message(client, userdata, msg):
    print("topic: " + msg.topic)
    print("payload: "+str(msg.payload))
    # message_data = json.loads(msg.payload)
    try:
        # Decode the JSON payload
        data = json.loads(msg.payload.decode())

        # Print the decoded JSON object
        # print("Received message on topic:", msg.topic)
        # print("JSON data:", data)
        topic = msg.topic
        status = data.get("status")
        doortype = data.get("doortype")
        message = data.get("message")
        print(f"Topic: {topic}")
        print(f"Status: {status}")
        print(f"DoorType: {doortype}")
        print(f"Message: {message}")

        # Save the received JSON data to a TXT file
        save_json_to_file(data)

        # Store the received JSON message in the global list
        received_messages.append({
            "timestamp": datetime.now(),
            "status": status,
            "doortype": doortype,
            "message": message
        })

        # Keep only the last 50 received messages
        if len(received_messages) > 50:
            received_messages.pop(0)

        # Save the last 50 messages to a CSV file
        save_messages_to_csv()

        # Send specific messages to the USB to serial adapter based on the door type
        if doortype == "FrontRightDoor":
            send_message_to_usb("410", "/dev/ttyACM0")  # Replace '/dev/ttyUSB0' with your USB to serial adapter port
            print("410 clicked")
        elif doortype == "FrontLeftDoor":
            send_message_to_usb("420", "/dev/ttyACM0")  # Replace '/dev/ttyUSB0' with your USB to serial adapter port
            print("420 clicked")
        elif doortype == "RearRightDoor":
            send_message_to_usb("430", "/dev/ttyACM0")  # Replace '/dev/ttyUSB0' with your USB to serial adapter port
            print("430 clicked")
        elif doortype == "RearLeftDoor":
            send_message_to_usb("440", "/dev/ttyACM0")  # Replace '/dev/ttyUSB0' with your USB to serial adapter port
            print("440 clicked")
        elif doortype == "BonnetLock":
            send_message_to_usb("460", "/dev/ttyACM0")
            print("460 clicked")
        elif doortype == "TrunkLock":
            send_message_to_usb("450", "/dev/ttyACM0")
            print("450 clicked")
        elif doortype == "CentralLock":
            send_message_to_usb("12", "/dev/ttyACM0")
            print("12 clicked")
        # Send Open close messages based on doortype and status
        elif doortype == "LDW":
            if message == "Unsubscribe":
                send_message_to_usb("100", "/dev/ttyACM0")
                print(f"100 clicked")
            elif message == "Subscribe":
                send_message_to_usb("101", "/dev/ttyACM0")
                print("101 clicked")
        elif doortype == "FCW":
            if message == "Unsubscribe":
                send_message_to_usb("200", "/dev/ttyACM0")
                print(f"200 clicked")
            elif message == "Subscribe":
                send_message_to_usb("201", "/dev/ttyACM0")
                print("201 clicked")
        elif doortype == "TPMS":
            if message == "Unsubscribe":
                send_message_to_usb("300", "/dev/ttyACM0")
                print(f"300 clicked")
            elif message == "Subscribe":
                send_message_to_usb("301", "/dev/ttyACM0")
                print("301 clicked")
        elif doortype == "DOOR":
            if message == "Unsubscribe":
                send_message_to_usb("400", "/dev/ttyACM0")
                print(f"400 clicked")
            elif message == "Subscribe":
                send_message_to_usb("401", "/dev/ttyACM0")
                print("401 clicked")
        elif doortype == "Temp":
            if message == "Increase":
                send_message_to_usb("6", "/dev/ttyACM0")
                print(f"600 clicked")
            elif message == "Decrease":
                send_message_to_usb("6", "/dev/ttyACM0")
                print("601 clicked")


    except json.JSONDecodeError as e:
        print(" ")


def save_json_to_file(data):
    folder_path = "updates"
    file_path = os.path.join(folder_path, "data.txt")

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)

    print(f"Saved JSON data to {file_path}")


def save_messages_to_csv():
    folder_path = "updates"
    file_path = os.path.join(folder_path, "data.csv")

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    if len(received_messages) == 0:
        return

    columns = ["timestamp", "status", "doortype", "message"]

    with open(file_path, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=columns)
        writer.writeheader()
        for message in received_messages:
            writer.writerow(message)

    print(f"Saved the last 50 messages to {file_path}")


def on_log(client, userdata, level, msg):
    print(msg.topic + " " + str(msg.payload))


mqttc = paho.Client()
mqttc.on_connect = on_connect
mqttc.on_message = on_message
mqttc.on_log = on_log

awshost = "a1w5rvqhps48wc-ats.iot.ap-south-1.amazonaws.com"
awsport = 8883
#clientId = "iotconsole-9c0322a7-ac38-42ba-b630-296c03b9b8ca"
clientId = "iotconsole-1f938eb7-3c59-4d33-b64d-9f9b2669e1f8"
thingName = "carDoor/status"
caPath = "./AmazonRootCA1.pem"
certPath = "./certificate.pem.crt"
keyPath = "./private.pem.key"

mqttc.tls_set(caPath, certfile=certPath, keyfile=keyPath, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2,
              ciphers=None)

mqttc.connect(awshost, awsport, keepalive=60)

mqttc.loop_forever()
