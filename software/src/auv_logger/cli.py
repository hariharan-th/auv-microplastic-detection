from __future__ import annotations
import argparse
import json
import logging
import time
from datetime import datetime, timezone

from .config import load_config
from .dashboard_server import serve_dashboard
from .mqtt_out import MqttOut
from .processing import describe_spectrum
from .sampler import Sampler
from .sensors import OpticalSensors
from .storage import Store
from .telemetry import ReadOnlyMavlink

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("auv_logger")


def main():
    parser = argparse.ArgumentParser(description="Offline-first AUV optical payload logger")
    parser.add_argument("--config", required=True, help="Path to YAML configuration")
    parser.add_argument("--dry-run", action="store_true", help="Use simulated sensor and sampler data")
    parser.add_argument("--host", default="127.0.0.1", help="Dashboard bind address (default: localhost only)")
    parser.add_argument("--port", type=int, default=8080, help="Dashboard HTTP port")
    parser.add_argument("command", choices=("run", "doctor", "dashboard"))
    args = parser.parse_args()
    cfg = load_config(args.config)
    dry = args.dry_run or cfg["system"].get("dry_run", False)
    if args.command == "doctor":
        print(json.dumps({"config": "loaded", "dry_run": dry, "serial_enabled": cfg["serial"].get("enabled", True),
                          "i2c_enabled": cfg["i2c"].get("enabled", True), "mavlink_enabled": cfg["mavlink"].get("enabled", False),
                          "mqtt_enabled": cfg["mqtt"].get("enabled", False)}, indent=2))
        return

    if args.command == "dashboard":
        serve_dashboard(cfg["system"]["database"], args.host, args.port)
        return

    store = Store(cfg["system"]["database"], cfg["system"]["csv_directory"])
    sensors = OpticalSensors(cfg["i2c"], dry_run=dry or not cfg["i2c"].get("enabled", True))
    sampler = Sampler(cfg["serial"], dry_run=dry or not cfg["serial"].get("enabled", True))
    telemetry = ReadOnlyMavlink(cfg["mavlink"])
    mqtt = MqttOut(cfg["mqtt"])
    telemetry.start()
    interval = max(1.0, float(cfg["system"]["sample_interval_s"]))
    try:
        while True:
            started = time.monotonic()
            sample_id = None
            try:
                sample_id = sampler.start(int(cfg["system"]["pump_duration_ms"]), float(cfg["system"]["measurement_timeout_s"]))
                data = sensors.read()
                data.update(describe_spectrum(data))
                data.update(telemetry.snapshot())
                if dry:
                    data["simulated"] = True
                timestamp = datetime.now(timezone.utc).isoformat()
                store.save(timestamp, cfg["system"]["vehicle_id"], sample_id, data)
                mqtt.publish(cfg["system"]["vehicle_id"], {"timestamp_utc": timestamp, "sample_id": sample_id, **data})
                log.info("recorded sample %s", sample_id)
            except Exception:
                log.exception("acquisition cycle failed; continuing after interval")
            finally:
                if sample_id:
                    sampler.finish(sample_id)
            time.sleep(max(0.0, interval - (time.monotonic() - started)))
    except KeyboardInterrupt:
        log.info("stopping logger")
    finally:
        telemetry.close()
        mqtt.close()
        sampler.close()
        sensors.close()
        store.close()


if __name__ == "__main__":
    main()
