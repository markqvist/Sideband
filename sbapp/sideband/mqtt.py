import RNS
import time
import threading
from collections import deque
from sbapp.mqtt import client as mqtt
from .sense import Telemeter, Commands

class MQTT():
    QUEUE_MAXLEN = 1024
    SCHEDULER_SLEEP = 1

    def __init__(self):
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.host = None
        self.port = None
        self.run = False
        self.is_connected = False
        self.queue_lock = threading.Lock()
        self.waiting_msgs = deque(maxlen=MQTT.QUEUE_MAXLEN)
        self.waiting_telemetry = set()
        self.unacked_msgs = set()
        self.client.user_data_set(self.unacked_msgs)
        self.client.on_connect_fail = self.connect_failed
        self.client.on_disconnect = self.disconnected
        self.start()

    def start(self):
        self.run = True
        threading.Thread(target=self.jobs, daemon=True).start()
        RNS.log("Started MQTT scheduler", RNS.LOG_DEBUG)

    def stop(self):
        RNS.log("Stopping MQTT scheduler", RNS.LOG_DEBUG)
        self.run = False

    def jobs(self):
        while self.run:
            try:
                if len(self.waiting_msgs) > 0:
                    RNS.log(f"Processing {len(self.waiting_msgs)} MQTT messages", RNS.LOG_DEBUG)
                    self.process_queue()
                    RNS.log("All MQTT messages processed", RNS.LOG_DEBUG)

            except Exception as e:
                RNS.log("An error occurred while running MQTT scheduler jobs: {e}", RNS.LOG_ERROR)
                RNS.trace_exception(e)

            time.sleep(MQTT.SCHEDULER_SLEEP)

        RNS.log("Stopped MQTT scheduler", RNS.LOG_DEBUG)

    def connect_failed(self, client, userdata):
        RNS.log(f"Connection to MQTT server failed", RNS.LOG_DEBUG)
        self.is_connected = False

    def disconnected(self, client, userdata, disconnect_flags, reason_code, properties):
        RNS.log(f"Disconnected from MQTT server, reason code: {reason_code}", RNS.LOG_EXTREME)
        self.is_connected = False

    def set_server(self, host, port):
        self.host = host
        self.port = port or 1883

    def set_auth(self, username, password):
        self.client.username_pw_set(username, password)

    def connect(self):
        RNS.log(f"Connecting MQTT server {self.host}:{self.port}", RNS.LOG_DEBUG) # TODO: Remove debug
        cs = self.client.connect(self.host, self.port)
        self.client.loop_start()

    def disconnect(self):
        RNS.log("Disconnecting from MQTT server", RNS.LOG_EXTREME) # TODO: Remove debug
        self.client.disconnect()
        self.client.loop_stop()
        self.is_connected = False

    def post_message(self, topic, data):
        mqtt_msg = self.client.publish(topic, data, qos=1)
        self.unacked_msgs.add(mqtt_msg.mid)
        self.waiting_telemetry.add(mqtt_msg)

    def process_queue(self):
        with self.queue_lock:
            self.connect()

            try:
                while len(self.waiting_msgs) > 0:
                    topic, data = self.waiting_msgs.pop()
                    self.post_message(topic, data)
            except Exception as e:
                RNS.log(f"An error occurred while publishing MQTT messages: {e}", RNS.LOG_ERROR)
                RNS.trace_exception(e)

            try:
                for msg in self.waiting_telemetry:
                    msg.wait_for_publish()
            except Exception as e:
                RNS.log(f"An error occurred while publishing MQTT messages: {e}", RNS.LOG_ERROR)
                RNS.trace_exception(e)

            self.disconnect()

    def handle(self, context_dest, telemetry):
        remote_telemeter = Telemeter.from_packed(telemetry)
        read_telemetry = remote_telemeter.read_all()
        telemetry_timestamp = read_telemetry["time"]["utc"]
        root_path = f"lxmf/telemetry/{RNS.prettyhexrep(context_dest)}"
        for sensor in remote_telemeter.sensors:
            s = remote_telemeter.sensors[sensor]
            topics = s.render_mqtt()
            if topics != None:
                for topic in topics:
                    topic_path = f"{root_path}/{topic}"
                    data = topics[topic]
                    self.waiting_msgs.append((topic_path, data))
                    # RNS.log(f"{topic_path}: {data}") # TODO: Remove debug
