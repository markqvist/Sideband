import RNS
import threading
from sbapp.mqtt import client as mqtt
from .sense import Telemeter, Commands

class MQTT():
    def __init__(self):
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.host = None
        self.port = None
        self.waiting_telemetry = set()
        self.unacked_msgs = set()
        self.client.user_data_set(self.unacked_msgs)
        # TODO: Add handling
        # self.client.on_connect_fail = mqtt_connection_failed
        # self.client.on_disconnect = disconnect_callback

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
        self.client.disconnect()
        self.client.loop_stop()

    def post_message(self, topic, data):
        mqtt_msg = self.client.publish(topic, data, qos=1)
        self.unacked_msgs.add(mqtt_msg.mid)
        self.waiting_telemetry.add(mqtt_msg)

    def handle(self, context_dest, telemetry):
        remote_telemeter = Telemeter.from_packed(telemetry)
        read_telemetry = remote_telemeter.read_all()
        telemetry_timestamp = read_telemetry["time"]["utc"]

        from rich.pretty import pprint
        pprint(read_telemetry)

        def mqtt_job():
            self.connect()
            root_path = f"lxmf/telemetry/{RNS.prettyhexrep(context_dest)}"
            for sensor in remote_telemeter.sensors:
                s = remote_telemeter.sensors[sensor]
                topics = s.render_mqtt()
                RNS.log(topics)

                if topics != None:
                    for topic in topics:
                        topic_path = f"{root_path}/{topic}"
                        data = topics[topic]
                        RNS.log(f"  {topic_path}: {data}")
                        self.post_message(topic_path, data)

            for msg in self.waiting_telemetry:
                msg.wait_for_publish()

            self.disconnect()

        threading.Thread(target=mqtt_job, daemon=True).start()