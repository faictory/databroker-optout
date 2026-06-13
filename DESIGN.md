# broker-removal-kit

An offline command-line kit that turns a pile of manually-collected people-search /
data-broker hits into a deduped, deadname-aware exposure audit, a set of ready-to-send
per-broker removal requests, and a status tracker that persists across runs.

---

## Interface Contract

### Charter

`broker-removal-kit` lets a doxxing-target individual (e.g. a trans person or LGBTQ+
journalist) feed in the data-broker listings they found by hand and, in one offline run,
get back a deduped exposure list with deadname matches flagged high-priority, a drafted
removal request for every broker, and a persistent removal tracker.

### Command Surface

The tool is invoked as `python -m broker_removal_kit <INPUT> [flags]`. There is one
command; it always performs the same audit-and-generate pass and reconciles the tracker.

| Token | Kind | Takes | Effect |
|-------|------|-------|--------|
| `<INPUT>` | positional arg (**required**) | path to a `.csv` or `.json` file of broker hits | Source records to audit. Format is auto-detected from the extension. Each record must carry at least the columns/keys `broker` and `name`. |
| `--config PATH` | flag | path to a TOML config file | Supplies the requester identity (`name`, `email`, `address`) used to fill removal requests, plus optional `deadnames` and a default output `dir`. |
| `--deadname NAME` | flag (repeatable) | a literal former-name / deadname string | Any exposure whose `name` or `aliases` contains this string (case-insensitive substring) is marked `high` priority. Merges with deadnames from `--config`. |
| `--out DIR` | flag | directory path (default `brk-out`) | Where `requests/` and `tracker.json` are written. Overrides the config `dir`. |
| `--format {text,json}` | flag | `text` (default) or `json` | Format of the summary printed to stdout. Files written to `--out` are unaffected. |
| `--mark BROKER=STATUS` | flag (repeatable) | `BROKER` is a broker name or slug; `STATUS` is `pending`, `submitted`, or `confirmed` | Transitions that broker's tracker entry to `STATUS` during this run; the change is written to `tracker.json` and persists. |
| `--version` | flag | — | Prints the tool version and the bundled broker-DB verification date, then exits 0. |
| `--help` / `-h` | flag | — | Prints usage listing every argument and flag, then exits 0. |

The broker opt-out procedures come from a **bundled, dated database** shipped inside the
package (no network access). `--config`, `--deadname`, `--out`, and `--mark` may all be
combined in a single run.

### Output schema / format

A run produces three things: (a) files under `--out`, and (b) a summary on stdout, and
(c) an exit code.

**Files written under `<out>/` (default `brk-out/`):**

- `requests/<broker-slug>.txt` — one plain-text removal request per distinct broker,
  populated from the bundled DB and (if given) the requester identity. Literal shape:

  ```
  To: privacy@spokeo.com
  Subject: Opt-out / record removal request — Spokeo
  Date: 2026-06-12
  Method: email        Opt-out URL: https://www.spokeo.com/optout
  (Broker procedure last verified: 2026-01-15)

  To whom it may concern,

  Under your published opt-out policy I request removal of the following
  record(s) listing my personal information on Spokeo:

    - Name shown: Jordan Rivera (also listed as: James Rivera)
      Location: Portland, OR    Listing: https://www.spokeo.com/Jordan-Rivera

  Please remove these record(s) and confirm in writing.

  Regards,
  Jordan Rivera <jordan@example.com>
  PO Box 1234, Portland, OR 97201
  ```

  When no requester identity is supplied, the signature fields render as the literal
  placeholders `<YOUR NAME>`, `<YOUR EMAIL>`, `<YOUR ADDRESS>`.

- `tracker.json` — the persistent status tracker, one entry per broker:

  ```json
  {
    "version": 1,
    "updated": "2026-06-12T17:30:00Z",
    "brokers": {
      "spokeo": {
        "broker": "Spokeo",
        "status": "pending",
        "exposure_ids": ["exp-001"],
        "request_file": "requests/spokeo.txt",
        "opt_out_url": "https://www.spokeo.com/optout",
        "history": [{ "status": "pending", "at": "2026-06-12T17:30:00Z" }]
      }
    }
  }
  ```

  On re-run, brokers already present keep their `status` and `history`; only new brokers
  are added at `pending` and `--mark` transitions are appended.

**Stdout summary (`--format text`, default):**

```
broker-removal-kit — exposure audit
input: examples/sample.csv  (6 rows, csv)
broker DB: 12 brokers, verified 2026-01-15

exposures: 4 unique  (2 rows deduped)
high priority: 1

  [HIGH] exp-001  Jordan Rivera — Portland, OR   sources: Spokeo, WhitePages   (deadname match: "James Rivera")
  [   ]  exp-002  Jordan Rivera — Seattle, WA     sources: BeenVerified
  [   ]  exp-003  A. Rivera — Portland, OR        sources: TruePeopleSearch
  [   ]  exp-004  Jordan Rivera — Eugene, OR      sources: Radaris

removal requests: 5 written → brk-out/requests/
  spokeo.txt  whitepages.txt  beenverified.txt  truepeoplesearch.txt  radaris.txt
tracker: brk-out/tracker.json  (5 pending · 0 submitted · 0 confirmed)
```

**Stdout summary (`--format json`):** a single JSON object —

```json
{
  "input": { "path": "examples/sample.csv", "rows": 6, "format": "csv" },
  "broker_db": { "brokers": 12, "verified": "2026-01-15" },
  "exposures": [
    { "id": "exp-001", "name": "Jordan Rivera", "location": "Portland, OR",
      "sources": ["Spokeo", "WhitePages"], "priority": "high",
      "deadname_matches": ["James Rivera"],
      "urls": ["https://www.spokeo.com/Jordan-Rivera", "https://www.whitepages.com/name/Jordan-Rivera"] }
  ],
  "summary": { "exposures": 4, "deduped_rows": 2, "high_priority": 1 },
  "requests": [{ "broker": "Spokeo", "slug": "spokeo", "file": "brk-out/requests/spokeo.txt" }],
  "tracker": { "path": "brk-out/tracker.json", "pending": 5, "submitted": 0, "confirmed": 0 }
}
```

**Exit codes:** `0` on a successful audit; `2` on a usage error or malformed input
(missing required column/key, unreadable file, bad `--mark`/`--format`/`STATUS` value),
with a one-line `error: ...` message on stderr.

### Default no-flag behavior

Running the tool with only the required input file and no flags performs the headline use
case end-to-end: ingest → normalize → dedupe → write per-broker removal requests → write
the tracker → print the summary.

```
$ python -m broker_removal_kit examples/sample.csv
broker-removal-kit — exposure audit
input: examples/sample.csv  (6 rows, csv)
broker DB: 12 brokers, verified 2026-01-15

exposures: 4 unique  (2 rows deduped)
high priority: 0

  [   ] exp-001  Jordan Rivera — Portland, OR   sources: Spokeo, WhitePages
  [   ] exp-002  Jordan Rivera — Seattle, WA     sources: BeenVerified
  [   ] exp-003  A. Rivera — Portland, OR        sources: TruePeopleSearch
  [   ] exp-004  Jordan Rivera — Eugene, OR      sources: Radaris

removal requests: 5 written → brk-out/requests/
  spokeo.txt  whitepages.txt  beenverified.txt  truepeoplesearch.txt  radaris.txt
tracker: brk-out/tracker.json  (5 pending · 0 submitted · 0 confirmed)
```

(With no `--deadname`/`--config`, nothing is flagged high priority and request
signatures use placeholders; everything else is identical.)

### Canonical invocations

1. **Full audit with identity + deadnames from config** (the `make run` smoke):
   ```
   $ python -m broker_removal_kit examples/sample.csv --config examples/brk.toml
   ...
   high priority: 1
     [HIGH] exp-001  Jordan Rivera — Portland, OR   sources: Spokeo, WhitePages   (deadname match: "James Rivera")
   removal requests: 5 written → brk-out/requests/
   ```

2. **Flag a deadname inline without a config file:**
   ```
   $ python -m broker_removal_kit examples/sample.csv --deadname "James Rivera"
   high priority: 1
     [HIGH] exp-001  Jordan Rivera — Portland, OR   sources: Spokeo, WhitePages   (deadname match: "James Rivera")
   ```

3. **Mark a request submitted; the status persists to the next run:**
   ```
   $ python -m broker_removal_kit examples/sample.csv --mark spokeo=submitted
   tracker: brk-out/tracker.json  (4 pending · 1 submitted · 0 confirmed)
   $ python -m broker_removal_kit examples/sample.csv          # re-run, no mark
   tracker: brk-out/tracker.json  (4 pending · 1 submitted · 0 confirmed)
   ```

4. **JSON summary into a chosen output directory:**
   ```
   $ python -m broker_removal_kit examples/sample.json --format json --out /tmp/audit
   { "input": { "path": "examples/sample.json", "rows": 6, "format": "json" }, ... }
   ```

5. **Malformed input is rejected:**
   ```
   $ python -m broker_removal_kit examples/bad-missing-name.csv
   error: input is missing required column 'name'
   $ echo $?
   2
   ```

### Acceptance criteria

Each criterion below is bound to exactly one command/flag; every item in the Command
Surface appears in at least one criterion.

- [ ] **`<INPUT>` (dedup):** given two input rows referencing the same record (same
  normalized name + location/age) across two brokers, the default run emits exactly **one**
  exposure entry whose `sources` cites **both** brokers.
- [ ] **`<INPUT>` (generation):** the default run writes exactly one
  `requests/<slug>.txt` file for **each distinct broker** present in the input, each
  populated from the bundled broker DB (recipient, opt-out URL, method, verified date).
- [ ] **`<INPUT>` (tracker init):** the default run writes `tracker.json` with one entry
  per distinct broker, all at status `pending`.
- [ ] **`<INPUT>` (malformed):** an input missing a required column/key (`broker` or
  `name`) is rejected with an `error:` message naming the missing field and exit code `2`.
- [ ] **`--deadname`:** an exposure whose name or aliases contains a string passed via
  `--deadname` is shown `[HIGH]` and gains a `deadname_matches` entry; without it, the
  same exposure is `[   ]`.
- [ ] **`--config`:** deadnames and requester identity supplied via `--config` are honored
  — the matching exposure is flagged `high` and the request signatures are filled with the
  requester `name`/`email`/`address` instead of placeholders.
- [ ] **`--out`:** `--out DIR` writes `requests/` and `tracker.json` under `DIR` instead of
  the default `brk-out/`.
- [ ] **`--format`:** `--format json` prints a single JSON summary object with
  `exposures`, `summary`, `requests`, and `tracker` keys; `--format text` (default) prints
  the human-readable report.
- [ ] **`--mark`:** `--mark <broker>=submitted` transitions that broker's tracker entry to
  `submitted`, and the new status is still present after a subsequent run with no `--mark`.
- [ ] **`--version`:** `--version` prints the tool version and bundled broker-DB date and
  exits `0`.
- [ ] **`--help`:** `--help`/`-h` prints usage listing every argument and flag and exits `0`.

## Coherence requirements (your design is REJECTED unless all hold)

(1) exactly one tool / one contract
(2) every criterion exercises THIS contract
(3) the default invocation demonstrates the headline
(4) NO second/competing contract or mode hiding

---

## Problem

84% of trans adults worry about online safety, and people-search / data-broker sites
expose deadnames and pre-transition records that are direct fuel for doxxing. Auditing
that exposure and filing removals today is a manual slog: a target searches dozens of
broker sites by hand, ends up with overlapping hits and no way to dedupe them, has to
hand-write each broker's opt-out request in that broker's required format, and then loses
track of which requests were sent or confirmed. There is no tooling that takes the records
a person already found and turns them into a deduped, prioritized, trackable removal
workflow. This hurts trans people, LGBTQ+ journalists, and other doxxing targets — the
people for whom a missed exposure is highest-stakes — by leaving a demoralizing chore
entirely manual.

## Goals / Non-goals

**Goals**

- Ingest user-collected broker hits (CSV or JSON) and normalize them into a clean record set.
- Dedupe records that refer to the same person across multiple brokers into single
  exposure entries that cite every source.
- Flag exposures that surface a configured deadname / former name as high priority.
- Generate a ready-to-send removal request per distinct broker, populated from a bundled,
  dated database of opt-out procedures.
- Maintain a removal-status tracker (`pending → submitted → confirmed`) that persists
  across runs.
- Run fully offline and reject malformed input clearly.

**Non-goals**

- **No live scraping or automated searching** — the user supplies the found records; the
  tool never touches a broker site.
- **No automated request submission / email sending** — the tool drafts requests; the user
  sends them.
- **No accounts, databases, or network services** — state is local files only.
- **No fuzzy/ML identity resolution** — dedup uses deterministic normalized keys, not
  probabilistic matching.
- **No GUI / web interface** — CLI only.
- **No maintenance of broker procedures as a live feed** — the DB is a bundled, dated
  snapshot; staleness is surfaced via its verified date, not auto-refreshed.

## Hermetic build constraints

- **Language / toolchain:** Python 3, packaged so `python -m broker_removal_kit` is the
  entrypoint; `ruff` for lint, `pytest` for tests. Permissive-licensed dependencies only
  (standard library plus, at most, a TOML reader on older Pythons).
- **Offline & secret-free:** builds and tests run with no network, no secrets, no paid
  services, and no real user data. The broker-procedure DB and all fixtures ship in-repo.
- **Licensing & docs:** ships an OSI-approved license (e.g. MIT) and a README documenting
  the command surface.
- **Makefile contract:** the repo's Makefile honors the canonical targets — `make check`
  (lint + test), `make test` (the suite), `make build` (install/compile, `pip install -e`),
  and `make run`. **`make run` invokes the real entrypoint on a bundled fixture**, namely:

  ```
  python -m broker_removal_kit examples/sample.csv --config examples/brk.toml
  ```

  where `examples/sample.csv` is the six-row fixture used throughout this document and
  `examples/brk.toml` carries a requester identity plus the deadname `"James Rivera"`. This
  produces real output — a deduped 4-exposure audit with one high-priority deadname match,
  five written removal requests, and a populated tracker — not a usage screen. Both
  fixtures ship in the repo under `examples/`.

## Test expectations

Every acceptance criterion is covered by at least one named test below.

**Unit**

- CSV and JSON ingestion produce identical normalized records from equivalent inputs.
- Normalization: case/whitespace folding and the dedup key (name + location/age) collapse
  matching rows and keep distinct rows separate (covers dedup AC; the negative case
  `A. Rivera` vs `Jordan Rivera` stays separate).
- Deadname matching is case-insensitive substring over name + aliases (covers `--deadname`).
- Broker-DB lookup returns recipient/method/URL/verified-date for a known broker and a
  defined fallback for an unknown broker.
- Request rendering fills requester identity from config and uses placeholders without it
  (covers `--config` identity path).
- Tracker reconcile preserves existing statuses on re-run and adds new brokers at `pending`.
- `--mark` parsing: valid `broker=status` applies; bad broker or bad status is an error.
- Input validation: missing `broker`/`name` raises the column-named error.

**Integration**

- Full default run on `examples/sample.csv` yields 4 exposures, 5 request files, and a
  `tracker.json` with 5 `pending` entries (covers `<INPUT>` generation + tracker init).
- `--config examples/brk.toml` flags `exp-001` high with `deadname match "James Rivera"`
  and fills request signatures.
- `--out DIR` writes `requests/` and `tracker.json` under the chosen directory.
- `--format json` emits a parseable object with the documented keys; `--format text` emits
  the human report.
- Persistence: a run with `--mark spokeo=submitted` followed by a plain re-run still shows
  Spokeo as `submitted` (covers `--mark` + tracker persistence).
- `--version` and `--help` print the documented content and exit 0.

**End-to-end**

- `make run` on the bundled fixtures exits 0 and prints a summary containing
  `high priority: 1`, `removal requests: 5 written`, and a non-empty tracker line (WORKS,
  not HOLLOW).
- A malformed fixture (`examples/bad-missing-name.csv`) run through the entrypoint prints
  the missing-column error to stderr and exits with code `2`.
