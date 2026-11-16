# Payload commissioning checklist

1. Review board datasheets and verify voltage, wiring, driver ratings, and output polarity before powering the assembly.
2. Flash the ESP32 with pump and laser loads disconnected. Confirm outputs remain off after reset; check serial startup and stop-button behavior.
3. Enable Pi I2C, verify sensor addresses, then run `auv-logger --config ../config/config.yaml doctor` and a dry-run before connecting loads.
4. Confirm SQLite and CSV records are created. If MQTT is enabled, verify local logging still works when the network is unavailable.
5. Check AS7265X channel order, dark/reference readings, LDR voltage, pump runtime, and laser shutdown in a controlled bench setup.
6. Test the sealed assembly and sampler in a supervised, shallow test environment only after the enclosure and electrical integration have been reviewed.

Record software versions, sensor conditions, and observed failures. Stop if outputs behave unexpectedly, a component overheats, or any water reaches electronics.
