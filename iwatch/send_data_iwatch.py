import paho.mqtt.client as mqtt
import json
import iwatch_simulator
import time
import socket
import ssl

# Replace with your own values
MQTT_BROKER_PORT = 8883  # SSL/TLS port
THING_ID = "org.Iotp2c:iwatch"
MQTT_TOPIC = f"{THING_ID}/things/twin/commands/modify"

def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker with result code " + str(rc))
    # Subscribe to the MQTT topic
    client.subscribe(MQTT_TOPIC)

def on_disconnect(client, userdata, rc):
    print("Disconnected from MQTT broker with result code " + str(rc))

def on_publish(client, userdata, mid):
    print("Message published to " + MQTT_TOPIC)

def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))

def send_data_to_ditto(iwatch_data):
    # Prepare the Ditto command payload
    ditto_data = {
        "topic": MQTT_TOPIC,
        "path": "/",
        "value": {
            "thingId": "org.Iotp2c:iwatch",
            "policyId": "org.Iotp2c:policy",
            "definition": "https://raw.githubusercontent.com/bernar0507/Eclipse-Ditto-MQTT-iWatch/main/iwatch/wot/iwatch.tm.jsonld",
            "attributes": {
                "heart_rate": iwatch_data['heart_rate'],
                "timestamp": iwatch_data['timestamp'],
                "longitude": iwatch_data['longitude'],
                "latitude": iwatch_data['latitude']
            }
        }
    }
    # Convert the dictionary to a JSON string
    ditto_data_str = json.dumps(ditto_data)

    # Publish the message to the MQTT topic
    client.publish(MQTT_TOPIC, payload=ditto_data_str)

    print("Data sent to Ditto: " + json.dumps(ditto_data))

def run_mqtt_client():
    # Create an MQTT client instance
    client = mqtt.Client()

    # Set the callbacks
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_publish = on_publish
    client.on_message = on_message

    # Load the self-signed certificate for verification
    client.tls_set("path/to/self_signed_certificate.crt", tls_version=ssl.PROTOCOL_TLSv1_2)

    # Allow insecure connections (optional, only for testing purposes)
    client.tls_insecure_set(True)

    # Set username and password
    client.username_pw_set(username='ditto', password='ditto')

    # Get the IP address of the MQTT broker
    broker_ip = socket.gethostbyname("mosquitto")

    # Connect to the MQTT broker
    print("Connecting to broker")
    client.connect(broker_ip, MQTT_BROKER_PORT, 60)

    # Start the MQTT client loop in a non-blocking manner
    client.loop_start()

    while True:
        iwatch_data = next(iwatch_simulator.iwatch(dict_dt))
        send_data_to_ditto(iwatch_data)
        time.sleep(1)

run_mqtt_client()
