import json
import os
from databroker_optout.errors import BrokerKitError
from databroker_optout import brokerdb


def parse_mark(raw):
    if '=' not in raw:
        raise BrokerKitError(f"invalid mark format: {raw} (expected BROKER=STATUS)")

    parts = raw.split('=', 1)
    broker = parts[0].strip()
    status = parts[1].strip()

    if status not in ('pending', 'submitted', 'confirmed'):
        raise BrokerKitError(f"invalid status: {status} (must be pending, submitted, or confirmed)")

    return {'broker': broker, 'status': status}


def reconcile(path, exposures, brokers, marks, now):
    existing_tracker = {}
    if os.path.exists(path):
        try:
            with open(path, 'r') as f:
                data = json.load(f)
                existing_tracker = data.get('brokers', {})
        except (json.JSONDecodeError, IOError):
            existing_tracker = {}

    marks_by_slug = {}
    for mark in marks:
        broker_name = mark['broker']
        status = mark['status']
        slug = brokerdb.slugify(broker_name)
        marks_by_slug[slug] = status
        db_entry = brokerdb.lookup(broker_name)
        if db_entry:
            canonical_slug = brokerdb.slugify(db_entry['name'])
            marks_by_slug[canonical_slug] = status

    new_brokers = {}

    for slug, broker_info in brokers.items():
        exposure_ids = broker_info.get('exposure_ids', [])
        if not exposure_ids:
            continue

        if slug in existing_tracker:
            existing = existing_tracker[slug]
            status = existing['status']
            history = existing['history']
        else:
            status = 'pending'
            history = [{'status': 'pending', 'at': now}]

        if slug in marks_by_slug:
            new_status = marks_by_slug[slug]
            if new_status != status:
                status = new_status
                history.append({'status': new_status, 'at': now})

        new_brokers[slug] = {
            'broker': broker_info['name'],
            'status': status,
            'exposure_ids': exposure_ids,
            'request_file': f"requests/{slug}.txt",
            'opt_out_url': broker_info.get('opt_out_url', ''),
            'history': history
        }

    tracker_data = {
        'version': 1,
        'updated': now,
        'brokers': new_brokers
    }

    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
    with open(path, 'w') as f:
        json.dump(tracker_data, f, indent=2)

    total_pending = 0
    total_submitted = 0
    total_confirmed = 0
    for broker_data in new_brokers.values():
        if broker_data['status'] == 'pending':
            total_pending += 1
        elif broker_data['status'] == 'submitted':
            total_submitted += 1
        elif broker_data['status'] == 'confirmed':
            total_confirmed += 1

    counts = {
        'pending': total_pending,
        'submitted': total_submitted,
        'confirmed': total_confirmed,
    }

    return counts
