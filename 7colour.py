import logging
import time

import paho.mqtt.client as mqtt
import requests
from inky.auto import auto
from PIL import Image

PI_URL = "192.168.0.2"
IMAGE_URL = f"http://{PI_URL}/7colour"
TOPIC = "7colour"
UPDATE_PAYLOAD = b"update"


logging.basicConfig(level=logging.DEBUG)


class ImageClient(mqtt.Client):
    def on_connect(self, mqttc, obj, flags, rc):
        logging.info("rc: " + str(rc))

    def on_connect_fail(self, mqttc, obj):
        logging.info("Connect failed")

    def on_message(self, mqttc, obj, msg):
        if msg.topic == TOPIC:
            logging.info(f"Message: {msg.payload}")
            if msg.payload == UPDATE_PAYLOAD:
                logging.info("Updating...")
                r = requests.get(IMAGE_URL, stream=True, timeout=2)
                if r.status_code == 200:
                    r.raw.decode_content = True
                    img = Image.open(r.raw).rotate(180)
                    self.display.set_image(img)
                    self.display.show()

    def on_publish(self, mqttc, obj, mid):
        logging.info("mid: " + str(mid))

    def on_subscribe(self, mqttc, obj, mid, granted_qos):
        logging.info("Subscribed: " + str(mid) + " " + str(granted_qos))

    def on_log(self, mqttc, obj, level, string):
        logging.info(string)

    def run(self):
        self.display = auto()
        self.connect(PI_URL, port=1883, keepalive=60)
        self.reconnect_delay_set(min_delay=1, max_delay=120)
        self.subscribe("#", 0)

        rc = 0
        while rc == 0:
            rc = self.loop()
        return rc


if __name__ == "__main__":
    client = ImageClient(TOPIC)

    while True:
        try:
            client.run()
        except KeyboardInterrupt:
            break
        except Exception as e:
            logging.error(e)
            logging.info("45 second backoff")
            time.sleep(45)
