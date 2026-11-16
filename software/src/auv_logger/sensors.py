from __future__ import annotations
import logging

log = logging.getLogger(__name__)
CHANNELS = ("410", "435", "460", "485", "510", "535", "560", "585", "610", "645", "680", "705", "730", "760", "810", "860", "900", "940")


class OpticalSensors:
    def __init__(self, cfg: dict, dry_run: bool = False):
        self.cfg = cfg
        self.dry_run = dry_run
        self.as7265x = None
        self.adc = None
        self.analog_in = None
        if dry_run:
            return
        import board
        import busio
        import qwiic_as7265x
        from adafruit_ads1x15 import ADS1115, AnalogIn, ads1x15

        i2c = busio.I2C(board.SCL, board.SDA)
        self.as7265x = qwiic_as7265x.QwiicAS7265x()
        if not self.as7265x.is_connected() or not self.as7265x.begin():
            raise RuntimeError("AS7265X not detected or failed initialization (expected address 0x49)")
        self.adc = ADS1115(i2c, address=int(cfg.get("ads1115_address", 0x48)))
        self.adc.gain = 1
        channel = int(cfg.get("ads1115_channel", 0))
        if channel not in range(4):
            raise ValueError("ADS1115 single-ended channel must be 0 through 3")
        self.analog_in = AnalogIn(self.adc, getattr(ads1x15.Pin, f"A{channel}"))

    def read(self) -> dict:
        if self.dry_run:
            return {f"as7265x_{name}_nm": None for name in CHANNELS} | {"ldr_raw": None, "ldr_voltage_v": None}
        self.as7265x.take_measurements()
        getters = ("a", "b", "c", "d", "e", "f", "g", "h", "r", "i", "s", "j", "t", "u", "v", "w", "k", "l")
        values = {f"as7265x_{nm}_nm": float(getattr(self.as7265x, f"get_calibrated_{getter}")())
                  for nm, getter in zip(CHANNELS, getters)}
        values["ldr_raw"] = int(self.analog_in.value)
        voltage = float(self.analog_in.voltage)
        values["ldr_voltage_v"] = voltage
        return values

    def close(self):
        pass
