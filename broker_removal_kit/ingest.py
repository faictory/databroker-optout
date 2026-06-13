import csv
import json
from pathlib import Path

from .errors import BrokerKitError


def load_records(path):
	"""
	Load records from a CSV or JSON file.

	Returns a tuple of (records, fmt, row_count) where:
	- records: list of dicts with broker, name, and optional fields
	- fmt: "csv" or "json"
	- row_count: number of records loaded

	Raises BrokerKitError if the file is unreadable, has an unrecognized
	extension, or is missing required columns/keys.
	"""
	path_obj = Path(path)

	# Detect format from extension
	suffix = path_obj.suffix.lower()
	if suffix == ".csv":
		fmt = "csv"
	elif suffix == ".json":
		fmt = "json"
	else:
		raise BrokerKitError(f"unrecognized file extension: {suffix}")

	# Try to read the file
	try:
		if fmt == "csv":
			records = _load_csv(path_obj)
		else:  # json
			records = _load_json(path_obj)
	except FileNotFoundError:
		raise BrokerKitError(f"input file not found: {path}")
	except (IOError, OSError) as e:
		raise BrokerKitError(f"error reading input file: {e}")
	except json.JSONDecodeError as e:
		raise BrokerKitError(f"invalid JSON: {e}")

	row_count = len(records)
	return records, fmt, row_count


def _load_csv(path):
	"""Load records from a CSV file."""
	records = []
	with open(path, "r", encoding="utf-8") as f:
		reader = csv.DictReader(f)
		if reader.fieldnames is None:
			raise BrokerKitError("csv file is empty")

		for row_num, row in enumerate(reader, start=2):  # start=2 because header is row 1
			record = _normalize_record(row, fmt="csv")
			records.append(record)

	return records


def _load_json(path):
	"""Load records from a JSON file."""
	with open(path, "r", encoding="utf-8") as f:
		data = json.load(f)

	if not isinstance(data, list):
		raise BrokerKitError("JSON input must be a list of objects")

	records = []
	for row_num, item in enumerate(data, start=1):
		if not isinstance(item, dict):
			raise BrokerKitError(f"JSON item {row_num} is not a dict")
		record = _normalize_record(item, fmt="json")
		records.append(record)

	return records


def _normalize_record(row, fmt):
	"""
	Normalize a record (dict) to ensure required fields and proper types.

	Validates that 'broker' and 'name' are present.
	Normalizes 'aliases' to a list.
	"""
	# Check required fields
	if "broker" not in row or row["broker"] is None:
		raise BrokerKitError("input is missing required column 'broker'")
	if "name" not in row or row["name"] is None:
		raise BrokerKitError("input is missing required column 'name'")

	# Start with the required fields
	record = {
		"broker": row["broker"],
		"name": row["name"],
	}

	# Add optional fields if present
	optional_fields = ["location", "age", "url"]
	for field in optional_fields:
		if field in row and row[field] is not None and row[field] != "":
			record[field] = row[field]

	# Handle aliases: normalize to list
	if "aliases" in row and row["aliases"] is not None and row["aliases"] != "":
		aliases = row["aliases"]
		if isinstance(aliases, list):
			# Already a list (from JSON)
			if aliases:  # Only include non-empty lists
				record["aliases"] = aliases
		elif isinstance(aliases, str):
			# String from CSV - could be comma or pipe delimited
			# Default to comma-delimited
			if aliases.strip():
				normalized = [a.strip() for a in aliases.split(",")]
				if normalized:  # Only include if not empty after normalization
					record["aliases"] = normalized

	return record
