import sys
import argparse
import json
from datetime import datetime
from zoneinfo import ZoneInfo

from broker_removal_kit import __version__, config, audit, summary, tracker, brokerdb, errors


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog='broker-removal-kit',
        description='Audit broker data exposures and generate removal requests',
        add_help=False,
    )

    parser.add_argument('input', nargs='?', help='Path to input CSV or JSON file')
    parser.add_argument(
        '--config',
        metavar='PATH',
        help='Path to TOML config file with requester identity and optional deadnames',
    )
    parser.add_argument(
        '--deadname',
        action='append',
        dest='deadnames',
        default=[],
        metavar='NAME',
        help='Mark exposures matching this deadname as high priority (repeatable)',
    )
    parser.add_argument(
        '--out',
        default=None,
        metavar='DIR',
        help='Output directory for requests/ and tracker.json (default: brk-out)',
    )
    parser.add_argument(
        '--format',
        default='text',
        choices=['text', 'json'],
        help='Output format: text or json (default: text)',
    )
    parser.add_argument(
        '--mark',
        action='append',
        dest='marks',
        default=[],
        metavar='BROKER=STATUS',
        help='Mark a broker as pending/submitted/confirmed (repeatable)',
    )
    parser.add_argument(
        '--version',
        action='store_true',
        help='Print version and broker DB date',
    )
    parser.add_argument(
        '-h', '--help',
        action='store_true',
        dest='show_help',
        help='Show this help message',
    )

    args = parser.parse_args(argv)

    # Handle --help
    if args.show_help:
        parser.print_help()
        return 0

    # Handle --version
    if args.version:
        db_date = brokerdb.verified_date()
        print(f"{__version__} (broker DB verified {db_date})")
        return 0

    # From here on, INPUT is required
    if not args.input:
        print("error: the following arguments are required: input", file=sys.stderr)
        return 2

    try:
        # Load config if provided
        identity = None
        config_deadnames = []
        config_out_dir = None

        if args.config:
            cfg = config.load_config(args.config)
            identity = {
                'name': cfg.get('name') or '<YOUR NAME>',
                'email': cfg.get('email') or '<YOUR EMAIL>',
                'address': cfg.get('address') or '<YOUR ADDRESS>',
            }
            config_deadnames = cfg.get('deadnames', [])
            config_out_dir = cfg.get('dir')

        # Merge deadnames: config deadnames + CLI deadnames
        all_deadnames = config_deadnames + args.deadnames

        # Resolve output directory: CLI --out overrides config dir
        out_dir = args.out or config_out_dir or 'brk-out'

        # Parse all --mark flags
        marks = []
        for mark_str in args.marks:
            mark = tracker.parse_mark(mark_str)
            marks.append(mark)

        # Generate timestamp
        now = datetime.now(ZoneInfo('UTC')).isoformat(timespec='seconds')

        # Run the audit
        result = audit.run_audit(args.input, identity, all_deadnames, out_dir, marks, now)

        # Format and print output
        if args.format == 'json':
            output = summary.format_json(result)
            print(json.dumps(output))
        else:
            output = summary.format_text(result)
            print(output)

        return 0

    except errors.BrokerKitError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
