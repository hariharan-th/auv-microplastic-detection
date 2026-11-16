# Hardware and software references

- SparkFun, [Spectral Triad (AS7265x) Hookup Guide](https://learn.sparkfun.com/tutorials/spectral-triad-as7265x-hookup-guide/all): board wiring, 3.3 V compatibility, I2C address and spectral channels.
- SparkFun, [Qwiic AS7265X Python Package](https://docs.sparkfun.com/qwiic_as7265x_py/): Raspberry Pi support, install command, API and 18 calibrated channels.
- Adafruit, [ADS1x15 library examples](https://docs.circuitpython.org/projects/ads1x15/en/stable/examples.html): ADS1115 Python API and `AnalogIn` voltage reading.
- Raspberry Pi, [Computer hardware documentation](https://www.raspberrypi.com/documentation/computers/raspberry-pi.html): 40-pin header, I2C and GPIO voltage limits.
- ArduPilot, [Requesting data from the autopilot](https://ardupilot.org/dev/docs/mavlink-requesting-data.html): telemetry streams and data link configuration. Follow the current autopilot manual for vehicle-specific setup and failsafes.

Confirm documentation and library versions against the exact installed hardware before deployment; vendor guides can change.
