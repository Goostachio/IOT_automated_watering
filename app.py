import time
import csv
from counterfit_connection import CounterFitConnection
import paho.mqtt.client as mqtt
from counterfit_shims_grove.grove_relay import GroveRelay
import json
from counterfit_shims_grove.adc import ADC
CounterFitConnection.init('127.0.0.1', 1883)

id = '49191e5e-c293-8ea8-93c0-81982693dd02'

client_telemetry_topic = id + '/telemetry'
server_command_topic = id + '/commands'
client_name = id + 'soilmoisturesensor_client'

def get_simulated_soil_moisture(file_path='/Users/daohongminh/Downloads/IOT/soimoi/moisture_level.csv'):
    if not hasattr(get_simulated_soil_moisture, 'line_index'):
        get_simulated_soil_moisture.line_index = 0

    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        lines = list(reader)
        soil_moisture = int(lines[get_simulated_soil_moisture.line_index][0])
        get_simulated_soil_moisture.line_index = (get_simulated_soil_moisture.line_index + 1) % len(lines)
        return soil_moisture

#adc = ADC()
relay = GroveRelay(0)

mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1,client_name)
mqtt_client.connect('test.mosquitto.org')

mqtt_client.loop_start()

print("MQTT connected!")

def handle_command(client, userdata, message):
    payload = json.loads(message.payload.decode())
    print("Message received:", payload)

    if payload['relay_on']:
        relay.on()
    else:
        relay.off()

mqtt_client.subscribe(server_command_topic)
mqtt_client.on_message = handle_command

while True:

    #soil_moisture = adc.read(0)
    soil_moisture = get_simulated_soil_moisture()
    print("Soil moisture:", soil_moisture)

    telemetry = json.dumps({'soil_moisture' : soil_moisture})
    print("sending telemetry: ", telemetry)

    mqtt_client.publish(client_telemetry_topic, telemetry )

    time.sleep(2)


