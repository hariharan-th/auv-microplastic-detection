from __future__ import annotations
import logging
import threading
import time

log = logging.getLogger(__name__)


class ReadOnlyMavlink:
    """Background MAVLink receiver; this class deliberately sends no messages."""
    def __init__(self, cfg: dict):
        self.cfg = cfg
        self.latest = {}
        self.stop_event = threading.Event()
        self.thread = None

    def start(self):
        if not self.cfg.get("enabled", False):
            return
        self.thread = threading.Thread(target=self._listen, daemon=True)
        self.thread.start()

    def _listen(self):
        try:
            from pymavlink import mavutil
            conn = mavutil.mavlink_connection(self.cfg["connection"], baud=int(self.cfg["baud"]))
            while not self.stop_event.is_set():
                msg = conn.recv_match(blocking=True, timeout=1)
                if msg is None:
                    continue
                kind = msg.get_type()
                d = msg.to_dict()
                if kind == "GLOBAL_POSITION_INT":
                    self.latest.update({"lat_deg": d["lat"] / 1e7, "lon_deg": d["lon"] / 1e7,
                                        "relative_alt_m": d["relative_alt"] / 1000.0,
                                        "heading_deg": d.get("hdg") / 100.0 if d.get("hdg", 65535) != 65535 else None})
                elif kind == "ATTITUDE":
                    self.latest.update({"roll_rad": d.get("roll"), "pitch_rad": d.get("pitch"), "yaw_rad": d.get("yaw")})
                elif kind == "VFR_HUD":
                    self.latest.update({"groundspeed_m_s": d.get("groundspeed"), "depth_or_alt_m": d.get("alt")})
                self.latest["telemetry_received_monotonic"] = time.monotonic()
        except Exception as exc:
            log.exception("MAVLink telemetry receiver stopped: %s", exc)

    def snapshot(self) -> dict:
        return dict(self.latest)

    def close(self):
        self.stop_event.set()
        if self.thread:
            self.thread.join(timeout=2)
