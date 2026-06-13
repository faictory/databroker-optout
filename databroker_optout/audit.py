import os
from databroker_optout import ingest, dedupe, deadname, requests, tracker, brokerdb


def run_audit(input_path, identity, deadnames, out_dir, marks, now):
    """
    Run the complete audit pipeline: ingest -> dedupe -> deadname -> request render -> tracker.

    Args:
        input_path: path to input CSV or JSON file
        identity: dict with 'name', 'email', 'address' (or None)
        deadnames: list of deadname strings (or empty list)
        out_dir: output directory for requests/ and tracker.json
        marks: list of parsed mark dicts [{'broker': ..., 'status': ...}, ...]
        now: ISO timestamp string (e.g., "2026-06-12T17:30:00Z")

    Returns:
        dict with keys: input, broker_db, exposures, summary, requests, tracker
    """
    # Load and parse input
    records, fmt, row_count = ingest.load_records(input_path)

    # Build exposures via deduplication
    exposures = dedupe.build_exposures(records)

    # Apply deadname priority marking
    deadname.apply_priority(exposures, deadnames)

    # Build a map of brokers from exposures (keyed by slug)
    brokers_dict = {}
    brokers_by_name = {}  # For easy lookup by original broker name
    for exposure in exposures:
        for record in exposure.get('records', []):
            broker_name = record.get('broker', '')
            if not broker_name:
                continue

            if broker_name not in brokers_by_name:
                # Look up broker in DB
                db_entry = brokerdb.lookup(broker_name)
                slug = brokerdb.slugify(db_entry['name'])
                brokers_dict[slug] = {
                    'name': db_entry['name'],
                    'slug': slug,
                    'db_entry': db_entry,
                    'exposure_ids': [],
                    'opt_out_url': db_entry.get('opt_out_url', ''),
                }
                brokers_by_name[broker_name] = brokers_dict[slug]

            # Add exposure id if not already present
            exp_id = exposure.get('id', '')
            if exp_id and exp_id not in brokers_by_name[broker_name]['exposure_ids']:
                brokers_by_name[broker_name]['exposure_ids'].append(exp_id)

    # Create requests/ directory
    requests_dir = os.path.join(out_dir, 'requests')
    os.makedirs(requests_dir, exist_ok=True)

    # Render and write request files
    request_files = []
    for slug, broker_info in brokers_dict.items():
        # Collect listings for this broker from exposures
        listings = []
        for exposure in exposures:
            for record in exposure.get('records', []):
                record_broker = record.get('broker', '')
                # Match by original name or canonical name
                broker_from_db = brokerdb.lookup(record_broker)
                if broker_from_db and brokerdb.slugify(broker_from_db['name']) == slug:
                    listing = {
                        'name': exposure.get('name', ''),
                        'aliases': exposure.get('aliases', []),
                        'location': record.get('location', ''),
                        'urls': [record.get('url', '')] if record.get('url') else [],
                        'url': record.get('url', ''),
                    }
                    listings.append(listing)

        # Render the request
        request_text = requests.render_request(
            broker_info['db_entry'],
            listings,
            identity,
            now.split('T')[0] if 'T' in now else now  # Extract date part
        )

        # Write to file
        file_path = os.path.join(requests_dir, f'{slug}.txt')
        with open(file_path, 'w') as f:
            f.write(request_text)

        request_files.append({
            'broker': broker_info['name'],
            'slug': slug,
            'file': f'requests/{slug}.txt',
        })

    # Reconcile tracker
    tracker_path = os.path.join(out_dir, 'tracker.json')
    tracker_counts = tracker.reconcile(tracker_path, exposures, brokers_dict, marks, now)

    # Build result dict
    deduped_rows = row_count - len(exposures)
    high_priority_count = sum(1 for exp in exposures if exp.get('priority') == 'high')

    result = {
        'input': {
            'path': input_path,
            'rows': row_count,
            'format': fmt,
        },
        'broker_db': {
            'brokers': brokerdb.broker_count(),
            'verified': brokerdb.verified_date(),
        },
        'exposures': exposures,
        'summary': {
            'exposures': len(exposures),
            'deduped_rows': deduped_rows,
            'high_priority': high_priority_count,
        },
        'requests': request_files,
        'tracker': {
            'path': tracker_path,
            'pending': tracker_counts['pending'],
            'submitted': tracker_counts['submitted'],
            'confirmed': tracker_counts['confirmed'],
        },
    }

    return result
