import json
import logging
import os

log = logging.getLogger(__name__)


class MqttOut:
    def __init__(self, cfg: dict):
        self.cfg = cfg
        self.client = None
        if not cfg.get("enabled", False):
            return
        import paho.mqtt.client as mqtt
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=cfg["client_id"])
        username = os.getenv(cfg.get("username_env", "AUV_MQTT_USERNAME"))
        password = os.getenv(cfg.get("password_env", "AUV_MQTT_PASSWORD"))
        if username:
            self.client.username_pw_set(username, password)
        if cfg.get("tls", True):
            ca = cfg.get("ca_file") or None
            self.client.tls_set(ca_certs=ca)
        self.client.connect(cfg["host"], int(cfg["port"]), keepalive=30)
        self.client.loop_start()

    def publish(self, vehicle_id: str, data: dict):
        if not self.client:
            return
        topic = f"{self.cfg['topic_prefix'].rstrip('/')}/{vehicle_id}/measurements"
        info = self.client.publish(topic, json.dumps(data, allow_nan=False), qos=1, retain=False)
        if info.rc != 0:
            log.warning("MQTT publish returned rc=%s; local record is retained", info.rc)

    def close(self):
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
