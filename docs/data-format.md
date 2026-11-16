# Data format

## Local storage

Each acquisition cycle creates a SQLite row and appends one row to `<csv_directory>/<vehicle_id>.csv`. The SQLite database stores the complete measurement as JSON plus timestamp, vehicle ID, and sample ID columns. Timestamps are UTC ISO-8601 strings.

Fields include `as7265x_<wavelength>_nm` for all 18 calibrated channels (wavelengths: 410, 435, 460, 485, 510, 535, 560, 585, 610, 645, 680, 705, 730, 760, 810, 860, 900, 940 nm), descriptive `spectrum_channel_count`, `spectrum_sum`, `spectrum_peak_nm`, and `spectrum_peak_value` features, `ldr_raw`, `ldr_voltage_v`, `sample_id`, and any latest available MAVLink telemetry such as position, relative altitude, heading, roll, pitch, and yaw. Null means no reading was available. The derived features are descriptive only and are not normalized to a microplastic concentration or polymer class.

## MQTT (optional)

When enabled, the logger publishes JSON to `<topic_prefix>/<vehicle_id>/measurements` with QoS 1 and no retained message. TLS is enabled by default. Credentials are read from the environment variable names in config; do not commit secrets or disable broker authentication on a public network. MQTT failure must not prevent local storage.

## Data quality recommendations

Keep raw values and provenance. Record firmware/software release, sensor serial number, integration time/illumination settings, calibration standards, sample location/depth source, water temperature, blanks, replicates, and any maintenance or cleaning. Keep analysis code separate from raw observations and document transformations.
