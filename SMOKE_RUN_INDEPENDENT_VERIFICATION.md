# Independent Smoke Run Verification — Clean State

## Verification Date
2026-06-13T04:20:12Z

## Verification Methodology
Starting from a completely clean state:
1. Removed all `brk-out/` directories and artifacts from any prior runs
2. Executed the documented smoke run entrypoint: `python -m databroker_optout examples/sample.csv --config examples/brk.toml`
3. Verified exit code (must be 0)
4. Verified all expected artifacts were generated under `brk-out/requests/` and `brk-out/tracker.json`
5. Verified the structure and content of generated files match expected schema

## Result
**STATUS: WORKS ✓**

The smoke run completes successfully from a clean state with all expected outputs and proper exit code.

## Detailed Verification Results

### Exit Code
```
0 (success)
```

### Stdout Output (Verbatim)
```
databroker-optout — exposure audit
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

### Generated Artifacts

**Request Files (5 total, all present):**
- ✓ `brk-out/requests/spokeo.txt` (761 bytes)
- ✓ `brk-out/requests/whitepages.txt` (652 bytes)
- ✓ `brk-out/requests/beenverified.txt` (620 bytes)
- ✓ `brk-out/requests/truepeoplesearch.txt` (632 bytes)
- ✓ `brk-out/requests/radaris.txt` (590 bytes)

All request files contain properly formatted email templates with correct recipient addresses, subject lines, method, and opt-out URLs from the bundled broker database.

**Tracker File:**
- ✓ `brk-out/tracker.json` (80 lines, valid JSON)
- Version: 1
- Updated timestamp: 2026-06-13T04:20:12+00:00
- 5 broker entries, all with status "pending"
- Correct exposure ID mappings:
  - spokeo: exp-001
  - whitepages: exp-001
  - beenverified: exp-002
  - truepeoplesearch: exp-003
  - radaris: exp-004
- Each broker contains:
  - `broker`: correct name
  - `status`: "pending"
  - `exposure_ids`: correct array
  - `request_file`: correct path
  - `opt_out_url`: correct URL from bundled broker DB
  - `history`: array with initial pending status and timestamp

### Test Suite Validation
- `make check`: All checks passed (ruff linting)
- `pytest`: 252 tests passed in 1.41s
  - All test modules passing
  - No failures, errors, or skipped tests
  - Covers all core functionality (audit, broker DB, CLI, config, deadname, dedupe, ingest, requests, tracker, etc.)

### Acceptance Criteria Validation
✓ Smoke run completes with exit 0 from a clean state
✓ All expected per-broker request files written under brk-out/requests/
✓ tracker.json properly initialized with 5 pending entries and correct schema
✓ Documented stdout summary emitted with all required fields
✓ No production code modifications required
✓ No network access required or attempted
✓ Complete test suite passes (252 tests)
✓ Run output captured as evidence (above)

## Conclusion

The databroker-optout smoke run is **fully functional and verified working** from a clean state. This independent verification confirms:
- The tool correctly ingests and normalizes the sample CSV
- Deduplication logic works correctly (2 rows deduped)
- Deadname detection and flagging works (HIGH priority correctly flagged)
- Per-broker removal request generation works with proper formatting
- Tracker initialization and JSON persistence works with correct schema
- Tool output is clear and complete
- Full test suite validates all components

**The smoke run justifies a WORKS verdict.**
