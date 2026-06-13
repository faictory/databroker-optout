import re
import json
import importlib.resources


def slugify(broker_name):
    return re.sub(r'[^a-z0-9]', '', broker_name.lower())


class BrokerDB:
    _instance = None

    def __init__(self):
        self._data = None

    def _load(self):
        if self._data is not None:
            return
        package_files = importlib.resources.files('databroker_optout')
        json_bytes = (package_files / 'brokers.json').read_text(encoding='utf-8')
        raw = json.loads(json_bytes)
        self._data = raw
        self._index = {}
        for broker in raw['brokers']:
            self._index[broker['name'].lower()] = broker
            self._index[broker['slug']] = broker

    def lookup(self, broker_name):
        self._load()
        key = broker_name.lower()
        if key in self._index:
            entry = self._index[key]
            return {
                'name': entry['name'],
                'recipient': entry['recipient'],
                'method': entry['method'],
                'opt_out_url': entry['opt_out_url'],
            }
        slug_key = slugify(broker_name)
        if slug_key in self._index:
            entry = self._index[slug_key]
            return {
                'name': entry['name'],
                'recipient': entry['recipient'],
                'method': entry['method'],
                'opt_out_url': entry['opt_out_url'],
            }
        return {
            'name': broker_name,
            'recipient': f'privacy@{slugify(broker_name)}.com',
            'method': 'email',
            'opt_out_url': '',
        }

    def verified_date(self):
        self._load()
        return self._data['verified']

    def broker_count(self):
        self._load()
        return len(self._data['brokers'])


_db = BrokerDB()


def lookup(broker_name):
    return _db.lookup(broker_name)


def verified_date():
    return _db.verified_date()


def broker_count():
    return _db.broker_count()
