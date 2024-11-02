from PIL import Image
import numpy as np
import paho.mqtt.client as mqtt
import json
import io
from picamera import PiCamera

def capture_image(crop_rectangle=None):
    """
    Captures an image from the Raspberry Pi camera and returns it as a PIL Image object.

    Parameters:
    - crop_rectangle: tuple, (left, upper, right, lower) for cropping. If None, no cropping is applied.

    Returns:
    - image: PIL Image object of the captured (and possibly cropped) image.
    """
    # Initialize the camera
    with PiCamera() as camera:
        # Configure camera settings if needed
        camera.resolution = (2592, 1944)  # Adjust resolution as needed
        camera.rotation = 0  # Adjust rotation if needed

        # Capture the image into a BytesIO stream
        stream = io.BytesIO()
        camera.capture(stream, format='jpeg')

    # Move the stream position to the beginning
    stream.seek(0)

    # Open the image with PIL
    image = Image.open(stream)

    image.save('/dev/shm/diesel_tank.jpg')

    # Crop the image if a crop rectangle is provided
    if crop_rectangle:
        image = image.crop(crop_rectangle)

    return image

def calculate_diesel_level(image, threshold=128):
    """
    Calculates the diesel level in a tank by determining the percentage of black pixels
    in a PIL Image after thresholding. Returns the percentage,
    the black and white image, and the cropped image before thresholding.

    Parameters:
    - image: PIL Image object to process.
    - threshold: int, grayscale threshold value (0-255) for converting to black and white.

    Returns:
    - diesel_level_percent: int, percentage of diesel level in the tank (rounded to the nearest integer).
    - bw_image: PIL Image object of the black and white image.
    """
    # Save the cropped image before thresholding
    cropped_image = image.copy()

    # Convert the image to grayscale
    gray_image = image.convert('L')

    # Convert the grayscale image to a NumPy array
    img_array = np.array(gray_image)

    # Apply the threshold to create a binary (black and white) image
    bw_array = img_array < threshold  # Pixels less than threshold are True (diesel)

    # Calculate the number of diesel pixels
    diesel_pixels = np.sum(bw_array)
    total_pixels = bw_array.size

    # Calculate the percentage of diesel level (rounded to the nearest integer)
    diesel_level_percent = int(round((diesel_pixels / total_pixels) * 100))

    # Invert the boolean array for correct black and white representation
    bw_image_array = np.where(bw_array, 0, 255).astype(np.uint8)  # True -> 0 (black), False -> 255 (white)
    bw_image = Image.fromarray(bw_image_array)

    return diesel_level_percent, bw_image, cropped_image

def publish_to_mqtt(diesel_level_percent, mqtt_config):
    """
    Publishes the diesel level percentage to an MQTT broker using Home Assistant's MQTT Discovery.

    Parameters:
    - diesel_level_percent: int, the diesel level percentage.
    - mqtt_config: dict, configuration parameters for the MQTT broker and Home Assistant discovery.
    """
    # MQTT Broker settings
    broker_address = mqtt_config['broker_address']
    broker_port = mqtt_config['broker_port']
    mqtt_user = mqtt_config['mqtt_user']
    mqtt_password = mqtt_config['mqtt_password']

    # Unique IDs and topics
    sensor_name = mqtt_config['sensor_name']
    unique_id = mqtt_config['unique_id']
    state_topic = mqtt_config['state_topic']
    config_topic = mqtt_config['config_topic']

    # Create MQTT client
    client = mqtt.Client()
    client.username_pw_set(username=mqtt_user, password=mqtt_password)

    # Connect to the broker
    client.connect(broker_address, broker_port, 60)

    # Home Assistant MQTT Discovery configuration payload
    config_payload = {
        "name": sensor_name,
        "state_topic": state_topic,
        "unit_of_measurement": "%",
        "value_template": "{{ value }}",
        "unique_id": unique_id,
        "icon": "mdi:gas-station",
        "force_update": "true",
        "availability_topic": mqtt_config['availability_topic'],
        "payload_available": "online",
        "payload_not_available": "offline"
        # Removed "device_class" and "state_class"
    }

    # Publish the configuration message
    client.publish(config_topic, json.dumps(config_payload), qos=1, retain=True)

    # Publish availability as online
    client.publish(mqtt_config['availability_topic'], "online", retain=True)

    # Publish the sensor's state
    client.publish(state_topic, diesel_level_percent, qos=1, retain=True)

    # Disconnect from the broker
    client.disconnect()

def main():
    # Define the crop rectangle (left, upper, right, lower)
    crop_rectangle = (60, 1060, 2590, 1100)

    # Define the threshold value
    threshold_value = 128  # Adjust as needed (0-255)

    # Capture the image from the Pi Camera
    image = capture_image(crop_rectangle)

    # Calculate the diesel level percentage and get the images
    diesel_level_percent, bw_image, cropped_image = calculate_diesel_level(
        image, threshold_value
    )

    # Save the cropped image before thresholding
    cropped_image.save('/dev/shm/diesel_crop.jpg')

    # Save the black and white image
    bw_image.save('/dev/shm/diesel_bw.jpg')

    # Output the result without decimals
    #print(f"Diesel level: {diesel_level_percent}%")

    # MQTT configuration
    mqtt_config = {
        "broker_address": "mqtt-broker-ip",
        "broker_port": 1883,
        "mqtt_user": "mqtt-user",
        "mqtt_password": "mqtt-password",
        "sensor_name": "Diesel Level",
        "unique_id": "diesel_level",
        "state_topic": "homeassistant/sensor/diesel_level/state",
        "config_topic": "homeassistant/sensor/diesel_level/config",
        "availability_topic": "homeassistant/sensor/diesel_level/availability"
    }

    # Publish the diesel level percentage to MQTT broker
    publish_to_mqtt(diesel_level_percent, mqtt_config)

if __name__ == "__main__":
    main()
