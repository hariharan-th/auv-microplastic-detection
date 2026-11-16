# Project summary

## Idea

An AUV payload for collecting water samples and recording optical measurements as an initial step toward microplastic monitoring.

## Implementation

An ESP32 controls the pump and laser via external drivers. A Raspberry Pi 4 reads the SparkFun AS7265X spectral sensor and an LDR through an ADS1115, computes basic descriptive features, timestamps and saves records locally, and optionally shares them using MQTT. A separate ArduSub-compatible autopilot controls vehicle movement; the logger can observe MAVLink telemetry only.

## Current limits

This version records optical signals but does not identify polymer types or calculate validated microplastic concentrations. Those claims need calibration, controlled sampling, and comparison with an appropriate laboratory method. Vehicle mechanical design and movement control are outside this payload repository.
