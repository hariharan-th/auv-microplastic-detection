from pathlib import Path
import yaml


def load_config(path: str) -> dict:
    config_path = Path(path).expanduser().resolve()
    with config_path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle) or {}
    config["_config_dir"] = str(config_path.parent)
    for section, key in (("system", "database"), ("system", "csv_directory")):
        raw = Path(config[section][key]).expanduser()
        if not raw.is_absolute():
            raw = Path(config["_config_dir"]) / raw
        config[section][key] = str(raw.resolve())
    return config
