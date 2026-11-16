# Payload safety

- The dedicated ArduSub-compatible autopilot controls vehicle movement. This project does not command propulsion; its MAVLink integration is receive-only.
- Test the sampler with pump and laser disconnected first. Never power either load directly from ESP32 GPIO; use suitable external drivers, fusing, and OFF-by-default behavior.
- Verify all board voltage ranges and common ground requirements. Raspberry Pi GPIO is 3.3 V and not 5 V tolerant; keep LDR/ADC signals within the ADS1115 supply range.
- Enclose the laser beam and prevent eye exposure. Disconnect power before wiring or servicing.
- Keep measurements local and do not rely on GSM, MQTT, or GNSS for underwater safety or recovery.
- Treat optical output as research data, not a confirmed microplastic identification or concentration.
