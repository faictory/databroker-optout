import json
import re
from importlib.resources import files


def slugify(broker_name):
    """Convert a broker name to a lowercase alphanumeric-only slug."""
    return re.sub(r'[^a-z0-9]', '', broker_name.lower())


class BrokerDB:
    def __init__(self):
        self._db = None
        self._broker_lookup = None

    def _load(self):
        """Load brokers.json from package data."""
        if self._db is not None:
            return

        # Load brokers.json from package data
        package_files = files('broker_removal_kit')
        brokers_file = package_files / 'brokers.json'
        data = json.loads(brokers_file.read_text(encoding='utf-8'))

        self._db = data

        # Build lookup maps: both by exact name and by slug
        self._broker_lookup = {}
        for broker in self._db['brokers']:
            name_lower = broker['name'].lower()
            self._broker_lookup[name_lower] = broker
            self._broker_lookup[broker['slug']] = broker

    def lookup(self, broker_name):
        """
        Look up a broker by name (case-insensitive) or slug.
        Returns a dict with recipient/method/opt_out_url/name.
        For unknown brokers, returns a fallback dict.
        """
        self._load()

        # Try to find by exact name (case-insensitive) or slug
        lookup_key = broker_name.lower()
        if lookup_key in self._broker_lookup:
            broker = self._broker_lookup[lookup_key]
            return {
                'name': broker['name'],
                'recipient': broker['recipient'],
                'method': broker['method'],
                'opt_out_url': broker['opt_out_url']
            }

        # Fallback for unknown broker
        return {
            'name': broker_name,
            'recipient': 'privacy@unknown.com',
            'method': 'email',
            'opt_out_url': ''
        }

    def verified_date(self):
        """Return the DB verification date."""
        self._load()
        return self._db['verified']

    def broker_count(self):
        """Return the total count of brokers in the DB."""
        self._load()
        return len(self._db['brokers'])


# Global singleton instance
_db = BrokerDB()


def lookup(broker_name):
    """Look up a broker by name or slug."""
    return _db.lookup(broker_name)


def verified_date():
    """Get the broker DB verification date."""
    return _db.verified_date()


def broker_count():
    """Get the total count of brokers in the DB."""
    return _db.broker_count()
