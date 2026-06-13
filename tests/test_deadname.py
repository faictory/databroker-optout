from databroker_optout.deadname import match_deadnames, apply_priority


class TestMatchDeadnames:
    def test_empty_deadnames_list_returns_empty(self):
        exposure = {"name": "Jordan Rivera", "aliases": ["James Rivera"]}
        assert match_deadnames(exposure, []) == []

    def test_name_match_case_insensitive(self):
        exposure = {"name": "Jordan Rivera", "aliases": []}
        assert match_deadnames(exposure, ["jordan rivera"]) == ["jordan rivera"]
        assert match_deadnames(exposure, ["JORDAN"]) == ["JORDAN"]
        assert match_deadnames(exposure, ["James"]) == []

    def test_alias_match_case_insensitive(self):
        exposure = {"name": "Jordan Rivera", "aliases": ["James Rivera"]}
        assert match_deadnames(exposure, ["james rivera"]) == ["james rivera"]
        assert match_deadnames(exposure, ["JAMES"]) == ["JAMES"]
        assert match_deadnames(exposure, ["Karen"]) == []

    def test_no_match_returns_empty_list(self):
        exposure = {"name": "Jordan Rivera", "aliases": ["James Rivera"]}
        assert match_deadnames(exposure, ["Karen", "Bob"]) == []

    def test_substring_match(self):
        exposure = {"name": "Jordan Rivera", "aliases": ["James Rivera"]}
        assert match_deadnames(exposure, ["jordan"]) == ["jordan"]
        assert match_deadnames(exposure, ["james"]) == ["james"]

    def test_multiple_deadnames_preserves_order(self):
        exposure = {"name": "Jordan Rivera", "aliases": ["James Rivera"]}
        result = match_deadnames(exposure, ["james", "jordan", "unknown"])
        assert result == ["james", "jordan"]

    def test_missing_aliases_field(self):
        exposure = {"name": "Jordan Rivera"}
        assert match_deadnames(exposure, ["jordan"]) == ["jordan"]

    def test_missing_name_field(self):
        exposure = {"aliases": ["James Rivera"]}
        assert match_deadnames(exposure, ["james"]) == ["james"]


class TestApplyPriority:
    def test_matching_exposure_marked_high(self):
        exposures = [{"name": "Jordan Rivera", "aliases": ["James Rivera"]}]
        apply_priority(exposures, ["james"])
        assert exposures[0]["priority"] == "high"
        assert exposures[0]["deadname_matches"] == ["james"]

    def test_non_matching_exposure_marked_normal(self):
        exposures = [{"name": "Jordan Rivera", "aliases": []}]
        apply_priority(exposures, ["james"])
        assert exposures[0]["priority"] == "normal"
        assert exposures[0]["deadname_matches"] == []

    def test_mix_of_matching_and_non_matching(self):
        exposures = [
            {"name": "Jordan Rivera", "aliases": ["James Rivera"]},
            {"name": "Alex Smith", "aliases": []},
            {"name": "Taylor Brown", "aliases": ["Kim Brown"]},
        ]
        apply_priority(exposures, ["james", "kim"])
        assert exposures[0]["priority"] == "high"
        assert exposures[0]["deadname_matches"] == ["james"]
        assert exposures[1]["priority"] == "normal"
        assert exposures[1]["deadname_matches"] == []
        assert exposures[2]["priority"] == "high"
        assert exposures[2]["deadname_matches"] == ["kim"]

    def test_apply_priority_returns_mutated_list(self):
        exposures = [{"name": "Jordan Rivera", "aliases": ["James Rivera"]}]
        result = apply_priority(exposures, ["james"])
        assert result is exposures

    def test_apply_priority_with_empty_deadnames(self):
        exposures = [{"name": "Jordan Rivera", "aliases": ["James Rivera"]}]
        apply_priority(exposures, [])
        assert exposures[0]["priority"] == "normal"
        assert exposures[0]["deadname_matches"] == []
