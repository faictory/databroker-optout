import json

from broker_removal_kit.summary import format_text, format_json


def test_format_text_basic():
    result = {
        "input": {"path": "examples/sample.csv", "rows": 6, "format": "csv"},
        "broker_db": {"brokers": 12, "verified": "2026-01-15"},
        "exposures": [
            {
                "id": "exp-001",
                "name": "Jordan Rivera",
                "location": "Portland, OR",
                "sources": ["Spokeo", "WhitePages"],
                "priority": "high",
                "deadname_matches": ["James Rivera"],
                "urls": []
            },
            {
                "id": "exp-002",
                "name": "Jordan Rivera",
                "location": "Seattle, WA",
                "sources": ["BeenVerified"],
                "priority": "normal",
                "deadname_matches": [],
                "urls": []
            },
            {
                "id": "exp-003",
                "name": "A. Rivera",
                "location": "Portland, OR",
                "sources": ["TruePeopleSearch"],
                "priority": "normal",
                "deadname_matches": [],
                "urls": []
            },
            {
                "id": "exp-004",
                "name": "Jordan Rivera",
                "location": "Eugene, OR",
                "sources": ["Radaris"],
                "priority": "normal",
                "deadname_matches": [],
                "urls": []
            }
        ],
        "summary": {"exposures": 4, "deduped_rows": 2, "high_priority": 1},
        "requests": [
            {"broker": "Spokeo", "slug": "spokeo", "file": "brk-out/requests/spokeo.txt"},
            {"broker": "WhitePages", "slug": "whitepages", "file": "brk-out/requests/whitepages.txt"},
            {"broker": "BeenVerified", "slug": "beenverified", "file": "brk-out/requests/beenverified.txt"},
            {"broker": "TruePeopleSearch", "slug": "truepeoplesearch", "file": "brk-out/requests/truepeoplesearch.txt"},
            {"broker": "Radaris", "slug": "radaris", "file": "brk-out/requests/radaris.txt"}
        ],
        "tracker": {"path": "brk-out/tracker.json", "pending": 5, "submitted": 0, "confirmed": 0}
    }

    output = format_text(result)

    assert "broker-removal-kit — exposure audit" in output
    assert "input: examples/sample.csv  (6 rows, csv)" in output
    assert "broker DB: 12 brokers, verified 2026-01-15" in output
    assert "exposures: 4 unique  (2 rows deduped)" in output
    assert "high priority: 1" in output
    assert "[HIGH] exp-001  Jordan Rivera — Portland, OR   sources: Spokeo, WhitePages   (deadname match: \"James Rivera\")" in output
    assert "[   ]  exp-002  Jordan Rivera — Seattle, WA     sources: BeenVerified" in output
    assert "[   ]  exp-003  A. Rivera — Portland, OR        sources: TruePeopleSearch" in output
    assert "[   ]  exp-004  Jordan Rivera — Eugene, OR      sources: Radaris" in output
    assert "removal requests: 5 written → brk-out/requests/" in output
    assert "tracker: brk-out/tracker.json  (5 pending · 0 submitted · 0 confirmed)" in output


def test_format_text_no_high_priority():
    result = {
        "input": {"path": "examples/sample.csv", "rows": 6, "format": "csv"},
        "broker_db": {"brokers": 12, "verified": "2026-01-15"},
        "exposures": [
            {
                "id": "exp-001",
                "name": "Jordan Rivera",
                "location": "Portland, OR",
                "sources": ["Spokeo", "WhitePages"],
                "priority": "normal",
                "deadname_matches": [],
                "urls": []
            }
        ],
        "summary": {"exposures": 1, "deduped_rows": 1, "high_priority": 0},
        "requests": [
            {"broker": "Spokeo", "slug": "spokeo", "file": "brk-out/requests/spokeo.txt"},
            {"broker": "WhitePages", "slug": "whitepages", "file": "brk-out/requests/whitepages.txt"}
        ],
        "tracker": {"path": "brk-out/tracker.json", "pending": 2, "submitted": 0, "confirmed": 0}
    }

    output = format_text(result)

    assert "high priority: 0" in output
    assert "[   ]  exp-001" in output
    assert "deadname match" not in output


def test_format_text_with_tracker_statuses():
    result = {
        "input": {"path": "examples/sample.csv", "rows": 6, "format": "csv"},
        "broker_db": {"brokers": 12, "verified": "2026-01-15"},
        "exposures": [],
        "summary": {"exposures": 0, "deduped_rows": 0, "high_priority": 0},
        "requests": [],
        "tracker": {"path": "brk-out/tracker.json", "pending": 4, "submitted": 1, "confirmed": 0}
    }

    output = format_text(result)

    assert "tracker: brk-out/tracker.json  (4 pending · 1 submitted · 0 confirmed)" in output


def test_format_json_basic():
    result = {
        "input": {"path": "examples/sample.csv", "rows": 6, "format": "csv"},
        "broker_db": {"brokers": 12, "verified": "2026-01-15"},
        "exposures": [
            {
                "id": "exp-001",
                "name": "Jordan Rivera",
                "location": "Portland, OR",
                "sources": ["Spokeo", "WhitePages"],
                "priority": "high",
                "deadname_matches": ["James Rivera"],
                "urls": ["https://www.spokeo.com/Jordan-Rivera", "https://www.whitepages.com/name/Jordan-Rivera"]
            },
            {
                "id": "exp-002",
                "name": "Jordan Rivera",
                "location": "Seattle, WA",
                "sources": ["BeenVerified"],
                "priority": "normal",
                "deadname_matches": [],
                "urls": []
            }
        ],
        "summary": {"exposures": 2, "deduped_rows": 1, "high_priority": 1},
        "requests": [
            {"broker": "Spokeo", "slug": "spokeo", "file": "brk-out/requests/spokeo.txt"},
            {"broker": "WhitePages", "slug": "whitepages", "file": "brk-out/requests/whitepages.txt"},
            {"broker": "BeenVerified", "slug": "beenverified", "file": "brk-out/requests/beenverified.txt"}
        ],
        "tracker": {"path": "brk-out/tracker.json", "pending": 3, "submitted": 0, "confirmed": 0}
    }

    output = format_json(result)

    assert "input" in output
    assert "broker_db" in output
    assert "exposures" in output
    assert "summary" in output
    assert "requests" in output
    assert "tracker" in output

    assert output["input"]["path"] == "examples/sample.csv"
    assert output["input"]["rows"] == 6
    assert output["input"]["format"] == "csv"

    assert output["broker_db"]["brokers"] == 12
    assert output["broker_db"]["verified"] == "2026-01-15"

    assert len(output["exposures"]) == 2
    assert output["exposures"][0]["id"] == "exp-001"
    assert output["exposures"][0]["name"] == "Jordan Rivera"
    assert output["exposures"][0]["location"] == "Portland, OR"
    assert output["exposures"][0]["sources"] == ["Spokeo", "WhitePages"]
    assert output["exposures"][0]["priority"] == "high"
    assert output["exposures"][0]["deadname_matches"] == ["James Rivera"]
    assert output["exposures"][0]["urls"] == ["https://www.spokeo.com/Jordan-Rivera", "https://www.whitepages.com/name/Jordan-Rivera"]

    assert output["summary"]["exposures"] == 2
    assert output["summary"]["deduped_rows"] == 1
    assert output["summary"]["high_priority"] == 1

    assert len(output["requests"]) == 3
    assert output["requests"][0]["broker"] == "Spokeo"
    assert output["requests"][0]["slug"] == "spokeo"
    assert output["requests"][0]["file"] == "brk-out/requests/spokeo.txt"

    assert output["tracker"]["path"] == "brk-out/tracker.json"
    assert output["tracker"]["pending"] == 3
    assert output["tracker"]["submitted"] == 0
    assert output["tracker"]["confirmed"] == 0

    json.dumps(output)


def test_format_json_missing_optional_fields():
    result = {
        "input": {"path": "examples/sample.json", "rows": 3, "format": "json"},
        "broker_db": {"brokers": 5, "verified": "2026-02-01"},
        "exposures": [
            {
                "id": "exp-001",
                "name": "Test User",
                "location": "Test City",
                "sources": ["Broker1"],
                "priority": "normal"
            }
        ],
        "summary": {"exposures": 1, "deduped_rows": 0, "high_priority": 0},
        "requests": [
            {"broker": "Broker1", "slug": "broker1", "file": "brk-out/requests/broker1.txt"}
        ],
        "tracker": {"path": "brk-out/tracker.json", "pending": 1, "submitted": 0, "confirmed": 0}
    }

    output = format_json(result)

    assert output["exposures"][0]["deadname_matches"] == []
    assert output["exposures"][0]["urls"] == []

    json.dumps(output)


def test_format_json_serializable():
    result = {
        "input": {"path": "examples/sample.csv", "rows": 6, "format": "csv"},
        "broker_db": {"brokers": 12, "verified": "2026-01-15"},
        "exposures": [
            {
                "id": "exp-001",
                "name": "Jordan Rivera",
                "location": "Portland, OR",
                "sources": ["Spokeo"],
                "priority": "normal"
            }
        ],
        "summary": {"exposures": 1, "deduped_rows": 0, "high_priority": 0},
        "requests": [
            {"broker": "Spokeo", "slug": "spokeo", "file": "brk-out/requests/spokeo.txt"}
        ],
        "tracker": {"path": "brk-out/tracker.json", "pending": 1, "submitted": 0, "confirmed": 0}
    }

    output = format_json(result)
    json_str = json.dumps(output)
    parsed = json.loads(json_str)

    assert parsed["input"]["path"] == "examples/sample.csv"
    assert parsed["exposures"][0]["id"] == "exp-001"
    assert parsed["requests"][0]["broker"] == "Spokeo"
