def match_deadnames(exposure, deadnames):
    """Perform case-insensitive substring matching of deadnames against exposure name and aliases.

    Args:
        exposure: dict-like object with 'name' and 'aliases' fields
        deadnames: list of deadname strings to match

    Returns:
        list of matched deadname strings in the order given, or empty list if no matches
    """
    if not deadnames:
        return []

    name_lower = exposure.get('name', '').lower()
    aliases_lower = [alias.lower() for alias in exposure.get('aliases', [])]

    matched = []
    for deadname in deadnames:
        deadname_lower = deadname.lower()
        if deadname_lower in name_lower or any(deadname_lower in alias for alias in aliases_lower):
            matched.append(deadname)

    return matched


def apply_priority(exposures, deadnames):
    """Mutate exposures to mark deadname matches as high priority.

    Args:
        exposures: list of exposure dicts
        deadnames: list of deadname strings

    Returns:
        the same exposures list (mutated in place)
    """
    for exposure in exposures:
        matches = match_deadnames(exposure, deadnames)
        if matches:
            exposure['priority'] = 'high'
            exposure['deadname_matches'] = matches
        else:
            exposure['priority'] = 'normal'
            exposure['deadname_matches'] = []

    return exposures
