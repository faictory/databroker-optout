# Smoke Run Results

## Command Invoked
```
python -m broker_removal_kit examples/sample.csv --config examples/brk.toml
```

## Working Directory
```
/Users/boldfield/.agentask/wt-worker-5-fAIctory-broker-removal-kit
```

## Exit Code
```
0 (success)
```

## Full Output (stdout)
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

## Resulting Output Tree
The smoke run created the following files:
- `brk-out/requests/spokeo.txt`
- `brk-out/requests/whitepages.txt`
- `brk-out/requests/beenverified.txt`
- `brk-out/requests/truepeoplesearch.txt`
- `brk-out/requests/radaris.txt`
- `brk-out/tracker.json` (5 pending removal requests, 0 submitted, 0 confirmed)

## Failure Mode
**The smoke run unexpectedly SUCCEEDS from clean checkout.** No errors, traceback, or failures detected. The tool correctly:
1. Parsed the CSV input
2. Identified 4 unique exposures from 6 input rows (2 rows deduped as duplicates)
3. Generated 5 removal request files
4. Created tracker.json with proper structure and status tracking
5. Exited with code 0

This suggests the smoke run is functioning as intended, contrary to the initial report that it was broken.
