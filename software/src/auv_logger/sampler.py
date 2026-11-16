from __future__ import annotations
import logging
import time
import uuid

log = logging.getLogger(__name__)


class Sampler:
    def __init__(self, cfg: dict, dry_run: bool = False):
        self.dry_run = dry_run or not cfg.get("enabled", True)
        self.ser = None
        if not self.dry_run:
            import serial
            self.ser = serial.Serial(cfg["port"], cfg["baudrate"], timeout=cfg["timeout_s"])
            time.sleep(2.0)
            self.ser.reset_input_buffer()

    def start(self, pump_ms: int, timeout_s: float) -> str:
        sample_id = uuid.uuid4().hex[:12]
        if self.dry_run:
            return sample_id
        self.ser.write(f"SAMPLE_START,{sample_id},{pump_ms}\n".encode("ascii"))
        deadline = time.monotonic() + timeout_s
        while time.monotonic() < deadline:
            line = self.ser.readline().decode("utf-8", "replace").strip()
            if line == f"ACK,{sample_id},STARTED":
                return sample_id
            if line.startswith("ERROR,"):
                raise RuntimeError(f"ESP32 rejected sample request: {line}")
        raise TimeoutError("ESP32 did not acknowledge sample request")

    def finish(self, sample_id: str):
        if not self.dry_run:
            self.ser.write(f"MEASURE_DONE,{sample_id}\n".encode("ascii"))

    def close(self):
        if self.ser:
            self.ser.close()
