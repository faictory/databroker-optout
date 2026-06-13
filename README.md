# databroker-optout

An offline tool for auditing personal data exposures across data brokers, generating removal requests, and tracking the status of your opt-out submissions.

## Purpose

`databroker-optout` helps you:
1. **Audit** your personal information across data brokers (offline, no network access)
2. **Generate** removal request letters pre-formatted with broker-specific contact info and opt-out procedures
3. **Track** the status of your removal requests (pending, submitted, confirmed) across runs

All broker opt-out procedures come from a bundled, dated database—no external network calls are made.

## License

MIT. See [LICENSE](LICENSE).

## Quick Start

```bash
make run
```

This runs the canonical smoke test with the bundled example:
```bash
python -m databroker_optout examples/sample.csv --config examples/brk.toml
```

## Invocation

```bash
python -m databroker_optout <INPUT> [flags]
```

`<INPUT>` is the **required** path to a `.csv` or `.json` file of broker hits. Format is auto-detected from the extension. Each record must have at least `broker` and `name` fields/columns.

## Flags

- `--config PATH` — Path to a TOML config file that supplies your requester identity (`name`, `email`, `address`), optional deadnames, and default output directory.
- `--deadname NAME` — Mark exposures with this name/alias as high priority (repeatable; case-insensitive substring match). Merges with deadnames from `--config`.
- `--out DIR` — Directory where `requests/` and `tracker.json` are written (default: `brk-out`). Overrides the config `dir`.
- `--format {text,json}` — Output format for the summary: `text` (default, human-readable) or `json` (structured object).
- `--mark BROKER=STATUS` — Transition a broker's tracker status to `pending`, `submitted`, or `confirmed` (repeatable). The change persists to `tracker.json`.
- `--version` — Print the tool version and bundled broker-DB verification date, then exit.
- `--help`, `-h` — Print usage with all arguments and flags, then exit.

## Output

Each run produces:

1. **Removal request files** — `<out>/requests/<broker-slug>.txt`, one per distinct broker, pre-filled with the broker's email, opt-out URL, and (if provided) your contact info.
2. **Tracker** — `<out>/tracker.json`, recording the status of each broker's removal request across runs.
3. **Summary** — Printed to stdout in `text` (default) or `json` format.

## Examples

**Basic audit (no config or deadnames):**
```bash
python -m databroker_optout examples/sample.csv
```

**With deadname flagging:**
```bash
python -m databroker_optout examples/sample.csv --deadname "James Rivera"
```

**Full audit with identity and deadnames from config:**
```bash
python -m databroker_optout examples/sample.csv --config examples/brk.toml
```

**Mark a broker's status as submitted (persists on re-run):**
```bash
python -m databroker_optout examples/sample.csv --mark spokeo=submitted
```

**JSON summary output:**
```bash
python -m databroker_optout examples/sample.csv --format json --out /tmp/audit
```

## Offline Operation

This tool operates entirely offline. All broker contact info, opt-out URLs, and verification dates are bundled in the package—no network access is required or attempted.
