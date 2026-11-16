# Payload architecture

This repository covers the latest project idea: an optical microplastic-monitoring payload built around the specified sensors and controllers.

- **Raspberry Pi 4:** reads the SparkFun AS7265X and LDR through an ADS1115, computes descriptive spectral features, logs locally to SQLite/CSV, and can publish records over MQTT.
- **ESP32 DevKit V2:** operates the sampling pump and laser through external drivers, with bounded pump runtime and a laser timeout.
- **Autopilot:** remains a separate, dedicated ArduSub-compatible controller. The Pi telemetry integration is receive-only; this code does not command propulsion.
- **Connectivity:** optional MQTT is intended for a network available at the surface. Local logging works without a network.

The spectral data and derived features are measurements for later analysis. They are not a validated microplastic classifier or concentration result. The design intentionally leaves vehicle mechanical, battery, propulsion, and navigation sizing to the vehicle integration work.
