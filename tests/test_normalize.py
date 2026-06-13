from broker_removal_kit.normalize import normalize_name, normalize_location, dedup_key


class TestNormalizeName:
    def test_case_fold(self):
        assert normalize_name("Jordan Rivera") == normalize_name("jordan rivera")
        assert normalize_name("JORDAN RIVERA") == normalize_name("jordan rivera")

    def test_collapse_whitespace(self):
        assert normalize_name("Jordan  Rivera") == normalize_name("Jordan Rivera")
        assert normalize_name("Jordan   Rivera") == normalize_name("Jordan Rivera")

    def test_strip_leading_trailing_whitespace(self):
        assert normalize_name("  Jordan Rivera  ") == normalize_name("Jordan Rivera")
        assert normalize_name("\tJordan Rivera\t") == normalize_name("Jordan Rivera")

    def test_punctuation_insensitive_spacing(self):
        assert normalize_name("A. Rivera") == normalize_name("A.Rivera")
        assert normalize_name("A . Rivera") == normalize_name("A.Rivera")
        assert normalize_name("A. Rivera") == "a.rivera"

    def test_non_string_input(self):
        assert normalize_name(None) == ""
        assert normalize_name(123) == ""
        assert normalize_name([]) == ""

    def test_multiple_punctuation(self):
        assert normalize_name("Smith, Jr.") == "smith,jr."
        assert normalize_name("Smith , Jr . ") == "smith,jr."


class TestNormalizeLocation:
    def test_location_uses_same_rules(self):
        assert normalize_location("Portland, OR") == normalize_location("portland, or")
        assert normalize_location("  Portland, OR  ") == normalize_location("Portland, OR")

    def test_non_string_location(self):
        assert normalize_location(None) == ""
        assert normalize_location(123) == ""


class TestDedupKey:
    def test_case_and_whitespace_only_difference_produces_same_key(self):
        record1 = {"name": "Jordan Rivera", "location": "Portland, OR"}
        record2 = {"name": "jordan rivera", "location": "portland, or"}
        assert dedup_key(record1) == dedup_key(record2)

    def test_case_and_whitespace_only_with_age(self):
        record1 = {"name": "Jordan Rivera", "location": "Portland, OR", "age": "35"}
        record2 = {"name": "jordan rivera", "location": "portland, or", "age": "35"}
        assert dedup_key(record1) == dedup_key(record2)

    def test_differing_name_produces_different_keys(self):
        record1 = {"name": "Jordan Rivera", "location": "Portland, OR"}
        record2 = {"name": "James Rivera", "location": "Portland, OR"}
        assert dedup_key(record1) != dedup_key(record2)

    def test_differing_location_produces_different_keys(self):
        record1 = {"name": "Jordan Rivera", "location": "Portland, OR"}
        record2 = {"name": "Jordan Rivera", "location": "Seattle, WA"}
        assert dedup_key(record1) != dedup_key(record2)

    def test_a_rivera_vs_jordan_rivera_same_city_stays_distinct(self):
        record1 = {"name": "A. Rivera", "location": "Portland, OR"}
        record2 = {"name": "Jordan Rivera", "location": "Portland, OR"}
        assert dedup_key(record1) != dedup_key(record2)

    def test_age_included_in_key(self):
        record1 = {"name": "Jordan Rivera", "location": "Portland, OR", "age": "35"}
        record2 = {"name": "Jordan Rivera", "location": "Portland, OR", "age": "36"}
        assert dedup_key(record1) != dedup_key(record2)

    def test_record_with_and_without_age_different(self):
        record1 = {"name": "Jordan Rivera", "location": "Portland, OR", "age": "35"}
        record2 = {"name": "Jordan Rivera", "location": "Portland, OR"}
        assert dedup_key(record1) != dedup_key(record2)

    def test_missing_name_field(self):
        record1 = {"location": "Portland, OR"}
        record2 = {"location": "Portland, OR"}
        assert dedup_key(record1) == dedup_key(record2)

    def test_empty_location(self):
        record1 = {"name": "Jordan Rivera", "location": ""}
        record2 = {"name": "jordan rivera", "location": ""}
        assert dedup_key(record1) == dedup_key(record2)

    def test_non_dict_input(self):
        assert dedup_key(None) is None
        assert dedup_key("not a dict") is None
        assert dedup_key([]) is None

    def test_deterministic_output(self):
        record = {"name": "Jordan Rivera", "location": "Portland, OR", "age": "35"}
        key1 = dedup_key(record)
        key2 = dedup_key(record)
        assert key1 == key2
        assert key1 is not key2  # Different tuple objects, but equal values

    def test_two_brokers_same_person_same_location(self):
        # Both records are for the same person in the same location
        spokeo_record = {"name": "Jordan Rivera", "location": "Portland, OR", "broker": "Spokeo"}
        whitepages_record = {"name": "jordan rivera", "location": "portland, or", "broker": "WhitePages"}
        assert dedup_key(spokeo_record) == dedup_key(whitepages_record)

    def test_same_person_different_locations(self):
        portland_record = {"name": "Jordan Rivera", "location": "Portland, OR"}
        seattle_record = {"name": "Jordan Rivera", "location": "Seattle, WA"}
        assert dedup_key(portland_record) != dedup_key(seattle_record)
