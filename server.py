import json
import time
import statistics

import paho.mqtt.client as mqtt
import threading

id = '49191e5e-c293-8ea8-93c0-81982693dd02'

client_telemetry_topic = id + '/telemetry'
server_command_topic = id + '/commands'
client_name = id + 'soilmoisturesensor_server'

mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1,client_name)
mqtt_client.connect('test.mosquitto.org')

mqtt_client.loop_start()

print("MQTT connected!")


num_iterations = 6
moisture_readings = []

def calculate_average_moisture_decrease():
    if len(moisture_readings) == num_iterations:
        differences = [moisture_readings[i-1] - moisture_readings[i] for i in range(1, num_iterations)]
        average_decrease = statistics.mean(differences)
        return average_decrease
    else:
        return None

def send_relay_command(client, state):
    command = {'relay_on': state}
    print("Sending message:", command)
    mqtt_client.publish(server_command_topic, json.dumps(command))


test_time = 1
watering_time=0
wait_time = 20
initial = False

def control_relay(client, initial):
    print("Unsubscribing from telemetry (stop measuring when watering)")
    mqtt_client.unsubscribe(client_telemetry_topic)

    if initial:
        water = test_time
    else:
        water = watering_time  # Calculated watering time based on average decrease
    
    print(f"Watering the plant for {water} seconds.")
    send_relay_command(client, True)
    time.sleep(water)
    send_relay_command(client, False)

    print("Wait time for moisture stabilization in the initial phase")
    time.sleep(wait_time)

    print("Subscribing to telemetry")
    mqtt_client.subscribe(client_telemetry_topic)




def handle_telemetry(client, userdata, message):
    payload = json.loads(message.payload.decode())
    print("Message received:", payload)
    
    global watering_time, initial, average_decrease

    if len(moisture_readings) < num_iterations:
        initial = True

        threading.Thread(target=control_relay, args=(client,initial)).start()
        moisture_readings.append(payload['soil_moisture'])
        average_decrease = calculate_average_moisture_decrease()
        print("average moisture reading decrease: ",average_decrease)

    elif payload['soil_moisture'] > 650:
        initial = False

        desired_moisture = 450
        watering_time = int((payload['soil_moisture'] - desired_moisture) / average_decrease)
        print("Updated watering time:", watering_time)
        threading.Thread(target=control_relay, args=(client,initial)).start()

mqtt_client.subscribe(client_telemetry_topic)
mqtt_client.on_message = handle_telemetry

while True:
    time.sleep(5)
