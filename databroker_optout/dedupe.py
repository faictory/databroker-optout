from databroker_optout.normalize import dedup_key


def build_exposures(records):
    """
    Group records by dedup_key and emit one exposure dict per group.
    Exposures are ordered by first-seen and have sequential ids.
    """
    if not records:
        return []

    groups = {}
    group_order = []

    for record in records:
        key = dedup_key(record)
        if key is None:
            continue

        if key not in groups:
            groups[key] = []
            group_order.append(key)

        groups[key].append(record)

    exposures = []
    for idx, key in enumerate(group_order):
        group = groups[key]
        first_record = group[0]

        exp_id = f"exp-{idx + 1:03d}"
        name = first_record.get("name", "")
        location = first_record.get("location", "")

        # Collect distinct brokers in first-seen order
        seen_brokers = {}
        sources = []
        for record in group:
            broker = record.get("broker", "")
            if broker and broker not in seen_brokers:
                seen_brokers[broker] = True
                sources.append(broker)

        # Collect all URLs
        urls = []
        for record in group:
            url = record.get("url", "")
            if url:
                urls.append(url)

        # Collect and dedupe aliases
        seen_aliases = {}
        aliases = []
        for record in group:
            record_aliases = record.get("aliases", [])
            if isinstance(record_aliases, str):
                record_aliases = [record_aliases] if record_aliases else []
            elif not isinstance(record_aliases, list):
                record_aliases = []

            for alias in record_aliases:
                alias_str = str(alias).strip() if alias else ""
                if alias_str and alias_str not in seen_aliases:
                    seen_aliases[alias_str] = True
                    aliases.append(alias_str)

        # Build records list with broker/url/location for each record
        records_list = []
        for record in group:
            records_list.append({
                "broker": record.get("broker", ""),
                "url": record.get("url", ""),
                "location": record.get("location", "")
            })

        exposure = {
            "id": exp_id,
            "name": name,
            "location": location,
            "aliases": aliases,
            "sources": sources,
            "urls": urls,
            "priority": "normal",
            "deadname_matches": [],
            "records": records_list
        }

        exposures.append(exposure)

    return exposures
