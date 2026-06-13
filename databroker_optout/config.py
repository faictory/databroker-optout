import sys
from typing import Dict, Any

from databroker_optout.errors import BrokerKitError

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


def load_config(path: str) -> Dict[str, Any]:
    try:
        with open(path, 'rb') as f:
            data = tomllib.load(f)
    except FileNotFoundError as e:
        raise BrokerKitError(f"config file not found: {path}") from e
    except tomllib.TOMLDecodeError as e:
        raise BrokerKitError(f"invalid TOML in config file: {e}") from e
    except Exception as e:
        raise BrokerKitError(f"failed to read config file: {e}") from e

    return {
        'name': data.get('name'),
        'email': data.get('email'),
        'address': data.get('address'),
        'deadnames': data.get('deadnames', []),
        'dir': data.get('dir'),
    }
