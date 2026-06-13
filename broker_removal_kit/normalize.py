import re


def normalize_name(name):
    """
    Fold case and collapse/strip whitespace with punctuation-insensitive spacing.
    Returns a canonical comparison form.
    """
    if not isinstance(name, str):
        return ""

    name = name.lower()

    # Collapse multiple spaces into single space
    name = re.sub(r'\s+', ' ', name)

    # Strip leading/trailing whitespace
    name = name.strip()

    # Trim punctuation-insensitive spacing: remove spaces around punctuation
    # This allows "A. Rivera" and "A. Rivera" to normalize identically
    # and handles cases like "A . Rivera" -> "a.rivera"
    name = re.sub(r'\s+([.,;:\-])', r'\1', name)
    name = re.sub(r'([.,;:\-])\s+', r'\1', name)

    return name


def normalize_location(location):
    """Normalize location using the same rules as normalize_name."""
    if not isinstance(location, str):
        return ""
    return normalize_name(location)


def dedup_key(record):
    """
    Build a deterministic key from normalized name combined with normalized location
    (and age when present) for deduplication.

    Returns a tuple that can be used as a dict key or for equality comparison.
    """
    if not isinstance(record, dict):
        return None

    # Extract and normalize name (required)
    name = record.get('name', '')
    normalized_name = normalize_name(name)

    # Extract and normalize location (optional)
    location = record.get('location', '')
    normalized_location = normalize_location(location)

    # Extract age (optional)
    age = record.get('age', '')
    if age:
        age = str(age).strip()

    # Build the key tuple
    if age:
        return (normalized_name, normalized_location, age)
    else:
        return (normalized_name, normalized_location)
