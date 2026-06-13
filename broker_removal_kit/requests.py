from broker_removal_kit.brokerdb import verified_date as get_verified_date


def render_request(broker_db_entry, listings, identity, date):
    """
    Render a plain-text removal request for a broker.

    Args:
        broker_db_entry: dict with 'name', 'recipient', 'method', 'opt_out_url',
                        and optionally 'verified_date'
        listings: list of dicts, each with 'name', 'aliases', 'location', 'url'
        identity: dict with 'name', 'email', 'address' (or None for placeholders)
        date: str in format 'YYYY-MM-DD'

    Returns:
        str: the complete removal request body
    """
    lines = []

    # Header lines
    lines.append(f"To: {broker_db_entry['recipient']}")
    lines.append(f"Subject: Opt-out / record removal request — {broker_db_entry['name']}")
    lines.append(f"Date: {date}")
    lines.append(f"Method: {broker_db_entry['method']}        Opt-out URL: {broker_db_entry['opt_out_url']}")

    # Verified date line
    verified_date_val = broker_db_entry.get('verified_date')
    if not verified_date_val:
        verified_date_val = get_verified_date()
    lines.append(f"(Broker procedure last verified: {verified_date_val})")

    lines.append("")
    lines.append("To whom it may concern,")
    lines.append("")
    lines.append("Under your published opt-out policy I request removal of the following")
    lines.append(f"record(s) listing my personal information on {broker_db_entry['name']}:")
    lines.append("")

    # Listing bullets
    for listing in listings:
        name = listing.get('name', '')
        aliases = listing.get('aliases', [])
        location = listing.get('location', '')
        url = listing.get('url', '')

        if aliases:
            aliases_str = ", ".join(aliases)
            lines.append(f"  - Name shown: {name} (also listed as: {aliases_str})")
        else:
            lines.append(f"  - Name shown: {name}")

        lines.append(f"    Location: {location}    Listing: {url}")

    lines.append("")
    lines.append("Please remove these record(s) and confirm in writing.")
    lines.append("")
    lines.append("Regards,")

    # Signature
    if identity:
        name = identity['name']
        email = identity['email']
        address = identity['address']
        lines.append(f"{name} <{email}>")
        lines.append(address)
    else:
        lines.append("<YOUR NAME> <<YOUR EMAIL>>")
        lines.append("<YOUR ADDRESS>")

    return "\n".join(lines)
