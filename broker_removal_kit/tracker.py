import json
import os
from broker_removal_kit.errors import BrokerKitError
from broker_removal_kit import brokerdb


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
                existing_tracker = data.get('exposures', {})
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

    new_exposures = {}

    for exposure in exposures:
        exp_id = exposure.get('id', '')
        if not exp_id:
            continue

        exposure_entry = {
            'exposure_id': exp_id,
            'name': exposure.get('name', ''),
            'location': exposure.get('location', ''),
            'aliases': exposure.get('aliases', []),
            'brokers': {}
        }

        seen_slugs = set()
        for record in exposure.get('records', []):
            broker_name = record.get('broker', '')
            if not broker_name:
                continue

            db_entry = brokerdb.lookup(broker_name)
            if not db_entry:
                continue

            slug = brokerdb.slugify(db_entry['name'])
            if slug not in brokers or slug in seen_slugs:
                continue

            seen_slugs.add(slug)
            broker_info = brokers[slug]

            if exp_id in existing_tracker and slug in existing_tracker[exp_id].get('brokers', {}):
                existing = existing_tracker[exp_id]['brokers'][slug]
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

            exposure_entry['brokers'][slug] = {
                'broker': broker_info['name'],
                'status': status,
                'request_file': f"requests/{slug}.txt",
                'opt_out_url': broker_info.get('opt_out_url', ''),
                'history': history
            }

        if exposure_entry['brokers']:
            new_exposures[exp_id] = exposure_entry

    tracker_data = {
        'version': 1,
        'updated': now,
        'exposures': new_exposures
    }

    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
    with open(path, 'w') as f:
        json.dump(tracker_data, f, indent=2)

    total_pending = 0
    total_submitted = 0
    total_confirmed = 0
    for exposure_data in new_exposures.values():
        for broker_info in exposure_data['brokers'].values():
            if broker_info['status'] == 'pending':
                total_pending += 1
            elif broker_info['status'] == 'submitted':
                total_submitted += 1
            elif broker_info['status'] == 'confirmed':
                total_confirmed += 1

    counts = {
        'pending': total_pending,
        'submitted': total_submitted,
        'confirmed': total_confirmed,
    }

    return counts
