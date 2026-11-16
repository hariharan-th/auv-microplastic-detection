from __future__ import annotations
import csv
import json
import sqlite3
from pathlib import Path


class Store:
    def __init__(self, db_path: str, csv_dir: str):
        self.db_path = Path(db_path)
        self.csv_dir = Path(csv_dir)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.csv_dir.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("""CREATE TABLE IF NOT EXISTS measurements (
            id INTEGER PRIMARY KEY, timestamp_utc TEXT NOT NULL, vehicle_id TEXT NOT NULL,
            sample_id TEXT, data_json TEXT NOT NULL)""")
        self.conn.commit()

    def save(self, timestamp: str, vehicle_id: str, sample_id: str | None, data: dict):
        payload = {"timestamp_utc": timestamp, "vehicle_id": vehicle_id, "sample_id": sample_id, **data}
        self.conn.execute("INSERT INTO measurements(timestamp_utc,vehicle_id,sample_id,data_json) VALUES(?,?,?,?)",
                          (timestamp, vehicle_id, sample_id, json.dumps(payload, allow_nan=False)))
        self.conn.commit()
        path = self.csv_dir / f"{vehicle_id}.csv"
        exists = path.exists()
        with path.open("a", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(payload.keys()), extrasaction="ignore")
            if not exists:
                writer.writeheader()
            writer.writerow(payload)

    def close(self):
        self.conn.close()
