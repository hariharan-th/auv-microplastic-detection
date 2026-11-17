# Local sample dashboard

The Raspberry Pi dashboard reads the `measurements` table created by the logger. It serves a browser page plus a read-only JSON endpoint at `/api/samples`. The page polls every five seconds, so new database rows appear shortly after acquisition. No third-party web framework or map service is required.

## Start

Install the package as described in the README. Keep the acquisition logger running in one terminal and start the dashboard in another:

```bash
auv-logger --config ../config/config.yaml run
auv-logger --config ../config/config.yaml dashboard
```

Open `http://127.0.0.1:8080` on the Raspberry Pi. To view it from another device on a trusted local network, bind it to the Pi's LAN interface or `0.0.0.0`, then open `http://<pi-address>:8080`. The service has no authentication or TLS. Do not expose it directly to the internet; use an authenticated private network or a properly secured reverse proxy if remote access is needed.

## Data behavior

- The API opens SQLite in read-only mode and does not change logger records.
- The latest 100 rows are returned in chronological order; the browser displays newest first.
- The display only shows fields already logged, including timestamps, sample IDs, vehicle IDs, optical channel count, and peak wavelength.
- MAVLink position is included in recorded rows when configured, but the current page does not invent a location when telemetry is unavailable.
- Dry-run records carry `simulated: true` and display a `SIMULATION` tag.
- The overview and research screenshots are design references. Values and labels shown inside them are not imported as field readings. The prototype photo is illustrative of the user's prototype and does not prove a live deployment.

This is an acquisition viewer, not a diagnostic service or a microplastic classifier. Optical peaks are not particle counts, polymer identification, or concentration. Validate scientific claims with controls, calibration, and independent laboratory analysis.
