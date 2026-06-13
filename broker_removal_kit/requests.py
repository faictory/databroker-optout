import broker_removal_kit.brokerdb as brokerdb


def render_request(broker_db_entry, listings, identity, date):
    """Return a plain-text removal request string for one broker."""
    broker_name = broker_db_entry['name']
    recipient = broker_db_entry['recipient']
    method = broker_db_entry['method']
    opt_out_url = broker_db_entry['opt_out_url']
    verified_date = broker_db_entry.get('verified_date') or brokerdb.verified_date()

    lines = []
    lines.append(f"To: {recipient}")
    lines.append(f"Subject: Opt-out / record removal request — {broker_name}")
    lines.append(f"Date: {date}")
    lines.append(f"Method: {method}        Opt-out URL: {opt_out_url}")
    lines.append(f"(Broker procedure last verified: {verified_date})")
    lines.append("")
    lines.append("To whom it may concern,")
    lines.append("")
    lines.append(
        f"Under your published opt-out policy I request removal of the following\n"
        f"record(s) listing my personal information on {broker_name}:"
    )
    lines.append("")

    for listing in listings:
        name_shown = listing.get('name', '')
        aliases = listing.get('aliases', [])
        location = listing.get('location', '')
        urls = listing.get('urls', [])
        url = urls[0] if urls else listing.get('url', '')

        name_line = f"  - Name shown: {name_shown}"
        if aliases:
            name_line += f" (also listed as: {', '.join(aliases)})"
        lines.append(name_line)

        detail_line = f"    Location: {location}    Listing: {url}"
        lines.append(detail_line)

    lines.append("")
    lines.append("Please remove these record(s) and confirm in writing.")
    lines.append("")
    lines.append("Regards,")

    if identity:
        requester_name = identity.get('name', '')
        requester_email = identity.get('email', '')
        requester_address = identity.get('address', '')
        lines.append(f"{requester_name} <{requester_email}>")
        lines.append(requester_address)
    else:
        lines.append("<YOUR NAME> <YOUR EMAIL>")
        lines.append("<YOUR ADDRESS>")

    return "\n".join(lines) + "\n"
