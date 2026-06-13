# Smoke Run Verification — Clean State

## Verification Date
2026-06-13T04:07:00Z

## Test Methodology
From a completely clean state (fresh checkout with no leftover artifacts):
1. Removed all `brk-out/` directories and previous state
2. Set up clean Python virtual environment
3. Executed: `python -m broker_removal_kit examples/sample.csv --config examples/brk.toml`
4. Verified exit code and all artifacts

## Result
**STATUS: WORKS ✓**

The smoke run completes successfully from a clean state with all expected outputs.

## Verification Results

### Exit Code
```
0 (success)
```

### Stdout Output
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

### Generated Artifacts

**Request Files (5 total, all present):**
- ✓ `brk-out/requests/spokeo.txt` (761 bytes)
- ✓ `brk-out/requests/whitepages.txt` (652 bytes)
- ✓ `brk-out/requests/beenverified.txt` (620 bytes)
- ✓ `brk-out/requests/truepeoplesearch.txt` (632 bytes)
- ✓ `brk-out/requests/radaris.txt` (590 bytes)

**Tracker File:**
- ✓ `brk-out/tracker.json` (1904 bytes)
- Structure: version 1, 5 broker entries, all at status "pending"
- Contains expected fields: broker, status, exposure_ids, request_file, opt_out_url, history

### Expected Output Validation
✓ Correct summary header ("broker-removal-kit — exposure audit")
✓ Input metadata line present
✓ Broker DB info line (12 brokers, verified 2026-01-15)
✓ Exposure counts correct (4 unique, 2 rows deduped)
✓ High priority count correct (1)
✓ Deadname match flagged ([HIGH] for exp-001, "James Rivera")
✓ All 5 exposure entries listed with correct formatting
✓ Removal requests summary present with file list
✓ Tracker summary with correct counts (5 pending, 0 submitted, 0 confirmed)

### Request File Quality
Verified spokeo.txt contains:
- Correct recipient email (privacy@spokeo.com)
- Subject line with broker name
- Current date
- Method and opt-out URL from bundled broker DB
- Broker verification date (2026-01-15)
- Properly formatted body with exposure details
- Requester identity filled from config (Jordan Rivera, email, address)
- Not using placeholder values

### Tracker JSON Validation
✓ Valid JSON structure
✓ Version field: 1
✓ Updated timestamp present
✓ 5 broker entries:
  - spokeo: pending, exp-001
  - whitepages: pending, exp-001
  - beenverified: pending, exp-002
  - truepeoplesearch: pending, exp-003
  - radaris: pending, exp-004
✓ Each broker has correct opt_out_url from bundled DB
✓ History records initial pending status with timestamp
✓ All exposure mappings correct

### Acceptance Criteria Met
✓ Clean-state run of bundled smoke entrypoint completes successfully
✓ Exit code is 0
✓ All expected request files written under brk-out/requests/
✓ tracker.json properly initialized with 5 pending entries
✓ Documented stdout summary emitted with all required fields
✓ No product code modifications
✓ No network access required or attempted
✓ All verification artifacts and exit code demonstrate true WORKS outcome

## Conclusion

The broker-removal-kit smoke run is **fully functional and healthy** from a clean state. All components are working as designed:
- CSV ingestion and normalization working correctly
- Deduplication logic functioning (2 rows deduped correctly)
- Deadname detection and flagging working (HIGH priority flagged for "James Rivera")
- Per-broker removal request generation working (5 files with proper formatting)
- Tracker initialization and persistence working (valid JSON with correct schema)
- Output summary complete and accurate

No issues detected. The tool is ready for use.
