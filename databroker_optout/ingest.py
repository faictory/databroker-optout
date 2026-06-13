import csv
import json
from pathlib import Path

from databroker_optout.errors import BrokerKitError


def load_records(path):
    file_path = Path(path)
    suffix = file_path.suffix.lower()

    if suffix == ".csv":
        return _load_csv(file_path)
    elif suffix == ".json":
        return _load_json(file_path)
    else:
        raise BrokerKitError(
            f"unrecognized file extension '{file_path.suffix}'; expected .csv or .json"
        )


def _load_csv(file_path):
    try:
        with open(file_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except (OSError, IOError) as e:
        raise BrokerKitError(f"cannot read input file '{file_path}': {e}") from e

    records = [_normalize_record(row) for row in rows]
    return records, "csv", len(rows)


def _load_json(file_path):
    try:
        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, IOError) as e:
        raise BrokerKitError(f"cannot read input file '{file_path}': {e}") from e
    except json.JSONDecodeError as e:
        raise BrokerKitError(f"invalid JSON in '{file_path}': {e}") from e

    if not isinstance(data, list):
        raise BrokerKitError(
            f"JSON input must be a list of objects, got {type(data).__name__}"
        )

    records = [_normalize_record(row) for row in data]
    return records, "json", len(data)


def _normalize_record(row):
    for field in ("broker", "name"):
        value = row.get(field)
        if value is None or not str(value).strip():
            raise BrokerKitError(f"input is missing required column '{field}'")

    aliases_raw = row.get("aliases", "")
    if isinstance(aliases_raw, list):
        aliases = [str(a).strip() for a in aliases_raw if str(a).strip()]
    else:
        aliases = [a.strip() for a in str(aliases_raw).split(",") if a.strip()]

    record = {
        "broker": str(row["broker"]).strip(),
        "name": str(row["name"]).strip(),
        "aliases": aliases,
    }

    for optional_field in ("location", "age", "url"):
        raw_value = row.get(optional_field)
        if raw_value is not None:
            stripped = str(raw_value).strip()
            if stripped:
                record[optional_field] = stripped

    return record
