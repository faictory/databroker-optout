import json
import pytest

from broker_removal_kit.errors import BrokerKitError
from broker_removal_kit.ingest import load_records


SAMPLE_CSV = "examples/sample.csv"
SAMPLE_JSON = "examples/sample.json"
BAD_MISSING_NAME = "examples/bad-missing-name.csv"


class TestLoadRecordsEquivalence:
    def test_csv_and_json_yield_same_row_count(self):
        csv_records, csv_fmt, csv_count = load_records(SAMPLE_CSV)
        json_records, json_fmt, json_count = load_records(SAMPLE_JSON)
        assert csv_count == json_count == 6

    def test_csv_format_tag(self):
        _, fmt, _ = load_records(SAMPLE_CSV)
        assert fmt == "csv"

    def test_json_format_tag(self):
        _, fmt, _ = load_records(SAMPLE_JSON)
        assert fmt == "json"

    def test_csv_and_json_records_match(self):
        csv_records, _, _ = load_records(SAMPLE_CSV)
        json_records, _, _ = load_records(SAMPLE_JSON)

        def sort_key(r):
            return (r["broker"], r["name"], r.get("url", ""))

        csv_sorted = sorted(csv_records, key=sort_key)
        json_sorted = sorted(json_records, key=sort_key)
        assert len(csv_sorted) == len(json_sorted)
        for csv_rec, json_rec in zip(csv_sorted, json_sorted):
            assert csv_rec["broker"] == json_rec["broker"]
            assert csv_rec["name"] == json_rec["name"]
            assert csv_rec.get("location") == json_rec.get("location")
            assert csv_rec.get("url") == json_rec.get("url")
            assert sorted(csv_rec["aliases"]) == sorted(json_rec["aliases"])


class TestAliasNormalization:
    def test_csv_comma_delimited_aliases_become_list(self):
        records, _, _ = load_records(SAMPLE_CSV)
        spokeo_records = [r for r in records if r["broker"] == "Spokeo"]
        for rec in spokeo_records:
            assert isinstance(rec["aliases"], list)
            assert "James Rivera" in rec["aliases"]

    def test_csv_empty_aliases_become_empty_list(self):
        records, _, _ = load_records(SAMPLE_CSV)
        been_verified = next(r for r in records if r["broker"] == "BeenVerified")
        assert been_verified["aliases"] == []

    def test_json_list_aliases_are_preserved(self):
        records, _, _ = load_records(SAMPLE_JSON)
        spokeo_records = [r for r in records if r["broker"] == "Spokeo"]
        for rec in spokeo_records:
            assert isinstance(rec["aliases"], list)
            assert "James Rivera" in rec["aliases"]

    def test_json_empty_list_aliases_stay_empty(self):
        records, _, _ = load_records(SAMPLE_JSON)
        been_verified = next(r for r in records if r["broker"] == "BeenVerified")
        assert been_verified["aliases"] == []


class TestRequiredColumnValidation:
    def test_missing_name_column_raises_broker_kit_error(self):
        with pytest.raises(BrokerKitError, match="name"):
            load_records(BAD_MISSING_NAME)

    def test_missing_broker_column_raises_broker_kit_error(self, tmp_path):
        bad_csv = tmp_path / "bad-broker.csv"
        bad_csv.write_text("name,location\nJordan Rivera,Portland OR\n")
        with pytest.raises(BrokerKitError, match="broker"):
            load_records(str(bad_csv))

    def test_empty_name_value_raises_broker_kit_error(self, tmp_path):
        bad_csv = tmp_path / "empty-name.csv"
        bad_csv.write_text("broker,name\nSpokeo,\n")
        with pytest.raises(BrokerKitError, match="name"):
            load_records(str(bad_csv))

    def test_empty_broker_value_raises_broker_kit_error(self, tmp_path):
        bad_csv = tmp_path / "empty-broker.csv"
        bad_csv.write_text("broker,name\n,Jordan Rivera\n")
        with pytest.raises(BrokerKitError, match="broker"):
            load_records(str(bad_csv))

    def test_missing_name_key_in_json_raises_broker_kit_error(self, tmp_path):
        bad_json = tmp_path / "bad.json"
        bad_json.write_text(json.dumps([{"broker": "Spokeo", "location": "Portland, OR"}]))
        with pytest.raises(BrokerKitError, match="name"):
            load_records(str(bad_json))

    def test_missing_broker_key_in_json_raises_broker_kit_error(self, tmp_path):
        bad_json = tmp_path / "bad.json"
        bad_json.write_text(json.dumps([{"name": "Jordan Rivera"}]))
        with pytest.raises(BrokerKitError, match="broker"):
            load_records(str(bad_json))


class TestFileErrors:
    def test_unrecognized_extension_raises_broker_kit_error(self, tmp_path):
        bad_file = tmp_path / "data.txt"
        bad_file.write_text("broker,name\n")
        with pytest.raises(BrokerKitError):
            load_records(str(bad_file))

    def test_missing_file_raises_broker_kit_error(self, tmp_path):
        nonexistent = tmp_path / "does-not-exist.csv"
        with pytest.raises(BrokerKitError):
            load_records(str(nonexistent))

    def test_invalid_json_raises_broker_kit_error(self, tmp_path):
        bad_json = tmp_path / "corrupt.json"
        bad_json.write_text("{not valid json}")
        with pytest.raises(BrokerKitError):
            load_records(str(bad_json))

    def test_json_non_list_raises_broker_kit_error(self, tmp_path):
        bad_json = tmp_path / "obj.json"
        bad_json.write_text(json.dumps({"broker": "Spokeo"}))
        with pytest.raises(BrokerKitError):
            load_records(str(bad_json))
