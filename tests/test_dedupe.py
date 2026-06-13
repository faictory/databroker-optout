from broker_removal_kit.dedupe import build_exposures


def test_empty_input():
    """Empty input returns empty list."""
    exposures = build_exposures([])
    assert exposures == []


def test_single_record():
    """Single record creates one exposure."""
    records = [
        {"broker": "Spokeo", "name": "Jordan Rivera", "location": "Portland, OR", "url": "https://spokeo.com/Jordan", "aliases": ""}
    ]
    exposures = build_exposures(records)

    assert len(exposures) == 1
    assert exposures[0]["id"] == "exp-001"
    assert exposures[0]["name"] == "Jordan Rivera"
    assert exposures[0]["location"] == "Portland, OR"
    assert exposures[0]["sources"] == ["Spokeo"]
    assert exposures[0]["urls"] == ["https://spokeo.com/Jordan"]
    assert exposures[0]["priority"] == "normal"
    assert exposures[0]["deadname_matches"] == []


def test_two_brokers_same_record():
    """Two records with same normalized name+location across two brokers produce one exposure citing both sources."""
    records = [
        {"broker": "Spokeo", "name": "Jordan Rivera", "location": "Portland, OR", "url": "https://spokeo.com/Jordan", "aliases": "James Rivera"},
        {"broker": "WhitePages", "name": "Jordan Rivera", "location": "Portland, OR", "url": "https://whitepages.com/Jordan", "aliases": "James Rivera"}
    ]
    exposures = build_exposures(records)

    assert len(exposures) == 1
    exp = exposures[0]
    assert exp["id"] == "exp-001"
    assert exp["name"] == "Jordan Rivera"
    assert exp["location"] == "Portland, OR"
    assert exp["sources"] == ["Spokeo", "WhitePages"]
    assert len(exp["urls"]) == 2
    assert "https://spokeo.com/Jordan" in exp["urls"]
    assert "https://whitepages.com/Jordan" in exp["urls"]
    assert len(exp["records"]) == 2


def test_distinct_records_sequential_ids():
    """Distinct records produce separate exposures with sequential IDs."""
    records = [
        {"broker": "Spokeo", "name": "Jordan Rivera", "location": "Portland, OR", "url": "https://spokeo.com/Jordan", "aliases": ""},
        {"broker": "BeenVerified", "name": "Jordan Rivera", "location": "Seattle, WA", "url": "https://beenverified.com/Jordan", "aliases": ""},
        {"broker": "TruePeopleSearch", "name": "A. Rivera", "location": "Portland, OR", "url": "https://truepeoplesearch.com/A", "aliases": ""}
    ]
    exposures = build_exposures(records)

    assert len(exposures) == 3
    assert exposures[0]["id"] == "exp-001"
    assert exposures[0]["name"] == "Jordan Rivera"
    assert exposures[0]["location"] == "Portland, OR"
    assert exposures[0]["sources"] == ["Spokeo"]

    assert exposures[1]["id"] == "exp-002"
    assert exposures[1]["name"] == "Jordan Rivera"
    assert exposures[1]["location"] == "Seattle, WA"
    assert exposures[1]["sources"] == ["BeenVerified"]

    assert exposures[2]["id"] == "exp-003"
    assert exposures[2]["name"] == "A. Rivera"
    assert exposures[2]["location"] == "Portland, OR"
    assert exposures[2]["sources"] == ["TruePeopleSearch"]


def test_alias_deduplication_strings():
    """Aliases are merged and deduplicated, handles string input."""
    records = [
        {"broker": "Spokeo", "name": "Jordan Rivera", "location": "Portland, OR", "url": "https://spokeo.com/Jordan", "aliases": "James Rivera"},
        {"broker": "WhitePages", "name": "Jordan Rivera", "location": "Portland, OR", "url": "https://whitepages.com/Jordan", "aliases": "James Rivera"}
    ]
    exposures = build_exposures(records)

    assert len(exposures) == 1
    assert exposures[0]["aliases"] == ["James Rivera"]


def test_alias_deduplication_list():
    """Aliases are merged and deduplicated, handles list input."""
    records = [
        {"broker": "Spokeo", "name": "Jordan Rivera", "location": "Portland, OR", "url": "https://spokeo.com/Jordan", "aliases": ["James Rivera", "Jim Rivera"]},
        {"broker": "WhitePages", "name": "Jordan Rivera", "location": "Portland, OR", "url": "https://whitepages.com/Jordan", "aliases": ["James Rivera"]}
    ]
    exposures = build_exposures(records)

    assert len(exposures) == 1
    aliases = exposures[0]["aliases"]
    assert len(aliases) == 2
    assert "James Rivera" in aliases
    assert "Jim Rivera" in aliases


def test_alias_deduplication_mixed():
    """Aliases merge correctly from mixed string/list inputs."""
    records = [
        {"broker": "Spokeo", "name": "Jordan Rivera", "location": "Portland, OR", "url": "https://spokeo.com/Jordan", "aliases": "James Rivera"},
        {"broker": "WhitePages", "name": "Jordan Rivera", "location": "Portland, OR", "url": "https://whitepages.com/Jordan", "aliases": ["James Rivera", "Jim Rivera"]}
    ]
    exposures = build_exposures(records)

    assert len(exposures) == 1
    aliases = exposures[0]["aliases"]
    assert len(aliases) == 2
    assert "James Rivera" in aliases
    assert "Jim Rivera" in aliases


def test_sources_first_seen_order():
    """Sources are listed in first-seen order."""
    records = [
        {"broker": "BeenVerified", "name": "Test User", "location": "City", "url": "https://been.com/test", "aliases": ""},
        {"broker": "Spokeo", "name": "Test User", "location": "City", "url": "https://spokeo.com/test", "aliases": ""},
        {"broker": "BeenVerified", "name": "Test User", "location": "City", "url": "https://been.com/test2", "aliases": ""}
    ]
    exposures = build_exposures(records)

    assert len(exposures) == 1
    assert exposures[0]["sources"] == ["BeenVerified", "Spokeo"]


def test_records_list_contents():
    """Records list retains broker/url/location for each record."""
    records = [
        {"broker": "Spokeo", "name": "Jordan Rivera", "location": "Portland, OR", "url": "https://spokeo.com/Jordan", "aliases": ""},
        {"broker": "WhitePages", "name": "Jordan Rivera", "location": "Portland, OR", "url": "https://whitepages.com/Jordan", "aliases": ""}
    ]
    exposures = build_exposures(records)

    assert len(exposures) == 1
    records_list = exposures[0]["records"]
    assert len(records_list) == 2

    assert records_list[0]["broker"] == "Spokeo"
    assert records_list[0]["url"] == "https://spokeo.com/Jordan"
    assert records_list[0]["location"] == "Portland, OR"

    assert records_list[1]["broker"] == "WhitePages"
    assert records_list[1]["url"] == "https://whitepages.com/Jordan"
    assert records_list[1]["location"] == "Portland, OR"


def test_dedup_key_with_age():
    """Records with same name+location+age are grouped together."""
    records = [
        {"broker": "Spokeo", "name": "John Smith", "location": "Boston, MA", "age": "42", "url": "https://spokeo.com/john", "aliases": ""},
        {"broker": "WhitePages", "name": "John Smith", "location": "Boston, MA", "age": "42", "url": "https://whitepages.com/john", "aliases": ""}
    ]
    exposures = build_exposures(records)

    assert len(exposures) == 1
    assert exposures[0]["sources"] == ["Spokeo", "WhitePages"]


def test_dedup_different_age():
    """Records with same name+location but different age are separate exposures."""
    records = [
        {"broker": "Spokeo", "name": "John Smith", "location": "Boston, MA", "age": "42", "url": "https://spokeo.com/john-42", "aliases": ""},
        {"broker": "WhitePages", "name": "John Smith", "location": "Boston, MA", "age": "45", "url": "https://whitepages.com/john-45", "aliases": ""}
    ]
    exposures = build_exposures(records)

    assert len(exposures) == 2
    assert exposures[0]["id"] == "exp-001"
    assert exposures[1]["id"] == "exp-002"


def test_normalization_punctuation():
    """Name normalization removes punctuation differences."""
    records = [
        {"broker": "Spokeo", "name": "A.Rivera", "location": "Portland, OR", "url": "https://spokeo.com/a", "aliases": ""},
        {"broker": "WhitePages", "name": "A. Rivera", "location": "Portland, OR", "url": "https://whitepages.com/a", "aliases": ""}
    ]
    exposures = build_exposures(records)

    assert len(exposures) == 1
    assert exposures[0]["sources"] == ["Spokeo", "WhitePages"]


def test_normalization_case():
    """Name normalization is case-insensitive."""
    records = [
        {"broker": "Spokeo", "name": "Jordan Rivera", "location": "Portland, OR", "url": "https://spokeo.com/jordan", "aliases": ""},
        {"broker": "WhitePages", "name": "JORDAN RIVERA", "location": "PORTLAND, OR", "url": "https://whitepages.com/jordan", "aliases": ""}
    ]
    exposures = build_exposures(records)

    assert len(exposures) == 1
    assert exposures[0]["sources"] == ["Spokeo", "WhitePages"]


def test_default_fields():
    """Default priority is 'normal', deadname_matches is empty."""
    records = [
        {"broker": "Spokeo", "name": "Test User", "location": "City", "url": "https://spokeo.com/test", "aliases": ""}
    ]
    exposures = build_exposures(records)

    assert exposures[0]["priority"] == "normal"
    assert exposures[0]["deadname_matches"] == []


def test_missing_optional_fields():
    """Records with missing optional fields are handled gracefully."""
    records = [
        {"broker": "Spokeo", "name": "Test User", "location": "City"},
        {"broker": "WhitePages", "name": "Test User", "location": "City", "url": "https://whitepages.com/test"}
    ]
    exposures = build_exposures(records)

    assert len(exposures) == 1
    assert exposures[0]["urls"] == ["https://whitepages.com/test"]
    assert exposures[0]["aliases"] == []


def test_deduped_rows_calculation():
    """Test data matches the expected dedup count."""
    records = [
        {"broker": "Spokeo", "name": "Jordan Rivera", "location": "Portland, OR", "url": "https://spokeo.com/jordan-1", "aliases": "James Rivera"},
        {"broker": "WhitePages", "name": "Jordan Rivera", "location": "Portland, OR", "url": "https://whitepages.com/jordan", "aliases": "James Rivera"},
        {"broker": "BeenVerified", "name": "Jordan Rivera", "location": "Seattle, WA", "url": "https://beenverified.com/jordan", "aliases": ""},
        {"broker": "TruePeopleSearch", "name": "A. Rivera", "location": "Portland, OR", "url": "https://truepeoplesearch.com/a", "aliases": ""},
        {"broker": "Radaris", "name": "Jordan Rivera", "location": "Eugene, OR", "url": "https://radaris.com/jordan", "aliases": ""},
        {"broker": "Spokeo", "name": "Jordan Rivera", "location": "Portland, OR", "url": "https://spokeo.com/jordan-2", "aliases": "James Rivera"}
    ]
    exposures = build_exposures(records)

    assert len(exposures) == 4
    deduped_rows = len(records) - len(exposures)
    assert deduped_rows == 2
