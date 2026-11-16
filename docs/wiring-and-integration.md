# Wiring and integration

Disconnect vehicle battery and remove propellers before wiring. Verify each board's exact silkscreen, voltage input range, and connector orientation. Raspberry Pi GPIO is 3.3 V and must never receive 5 V.

## Raspberry Pi 4 sensor bus

Use one I2C bus for the SparkFun AS7265X and ADS1115. The Pi 4 physical header pins are:

| Raspberry Pi 4 | Signal | AS7265X Qwiic | ADS1115 |
|---|---|---|---|
| Pin 1 | 3.3 V | 3V3/VIN as board documentation specifies | VDD |
| Pin 3 / GPIO2 | SDA | SDA | SDA |
| Pin 5 / GPIO3 | SCL | SCL | SCL |
| Pin 6 | GND | GND | GND |
| — | — | Qwiic connector or compatible 4-pin adapter | A0 ← LDR AO |

LDR module: power from 3.3 V only if its module accepts that supply; connect GND common and AO to ADS1115 A0. Leave DO unused. Confirm the AO output cannot exceed ADS1115 VDD. Never connect the LDR's analog output to a Pi GPIO. Tie all I2C grounds together. Enable I2C using `sudo raspi-config`; scan with `i2cdetect -y 1`. SparkFun AS7265X default address is 0x49; ADS1115 commonly uses 0x48 but verify the module address straps.

Power the sensor board with an adequately rated 3.3 V supply/appropriate Qwiic adapter, not a Pi pin if total sensor/illumination current exceeds that pin's budget. The AS7265X onboard illumination LEDs can have substantial current draw. Keep supply and ground wiring short and decouple per board documentation.

## Pi to ESP32

Connect ESP32 to Pi by USB. The Pi opens the enumerated serial device at 115200 baud. Do not wire Pi GPIO UART directly to an ESP32 board until voltage levels and ground/reference are confirmed. Protocol is newline-delimited UTF-8 ASCII:

- Pi → ESP32: `SAMPLE_START,<id>,<pump_ms>`
- ESP32 → Pi: `ACK,<id>,STARTED`
- Pi → ESP32 after optical reading: `MEASURE_DONE,<id>`
- ESP32 events: `EVENT,<id>,LASER_ON`, `PUMP_TIMEOUT_OFF`, `COMPLETE`, or `BUTTON_ABORT`

Pump duration is limited in firmware to 5000 ms. Laser has a 30-second hard timeout and remains enabled only until `MEASURE_DONE`, a stop-button press, reset, or power loss. Verify output polarity with a meter/LED before connecting loads.

## ESP32 output stage

| Function | ESP32 pin | External circuit |
|---|---:|---|
| Stop button | GPIO27 to GND, internal pull-up | momentary normally-open switch; firmware treats press as stop-only |
| Pump driver control | GPIO25 | logic-level MOSFET driver or rated motor driver; external pump supply |
| Laser driver control | GPIO26 | suitable constant-current/laser driver with enable input |

GPIO pins cannot supply pump or laser current. Use a correctly rated driver, fuse each load supply, provide common control ground where the driver topology requires it, and add motor flyback suppression as appropriate. Avoid powering a motor from the ESP32 regulator. Make driver hardware default OFF during reset/brownout. Confirm whether the driver's enable input is active high; adjust `PUMP_ACTIVE_HIGH` and `LASER_ACTIVE_HIGH` only after bench verification. Use an eye-safe, enclosed, low-power optical source; never look into the beam.

## Autopilot / vehicle interface

Connect the Pi to a dedicated telemetry output configured to provide status messages, using a correctly voltage-matched USB telemetry adapter or isolated interface. Configure receive-only access where practical. This logger does not transmit MAVLink commands, but physical/link-level separation and autopilot failsafe configuration remain the system integrator's responsibility. Never combine sampler control pins with ESC/thruster wiring.

## Surface communications

Put GSM/LTE modem, antenna, and GNSS antenna on a surface float or topside station with suitable sealing and strain relief. Underwater sampling remains offline-capable; the logger queues data locally and optional MQTT publishes when a link is available.
