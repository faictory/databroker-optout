import json
import tempfile
from databroker_optout.cli import main


class TestJsonFormat:
    def test_format_json_on_sample_csv(self, capsys):
        with tempfile.TemporaryDirectory() as out_dir:
            result = main(['examples/sample.csv', '--format', 'json', '--out', out_dir])
            assert result == 0
            captured = capsys.readouterr()
            output = json.loads(captured.out)

            # Verify all required keys are present
            assert 'input' in output
            assert 'broker_db' in output
            assert 'exposures' in output
            assert 'summary' in output
            assert 'requests' in output
            assert 'tracker' in output

    def test_json_output_is_single_object(self, capsys):
        with tempfile.TemporaryDirectory() as out_dir:
            result = main(['examples/sample.csv', '--format', 'json', '--out', out_dir])
            assert result == 0
            captured = capsys.readouterr()
            output = json.loads(captured.out)

            # Verify it's a dict, not a list
            assert isinstance(output, dict)

    def test_json_input_key_structure(self, capsys):
        with tempfile.TemporaryDirectory() as out_dir:
            result = main(['examples/sample.csv', '--format', 'json', '--out', out_dir])
            assert result == 0
            captured = capsys.readouterr()
            output = json.loads(captured.out)

            # Verify input key has expected fields
            assert 'path' in output['input']
            assert 'rows' in output['input']
            assert 'format' in output['input']
            assert 'sample.csv' in output['input']['path']

    def test_json_broker_db_key_structure(self, capsys):
        with tempfile.TemporaryDirectory() as out_dir:
            result = main(['examples/sample.csv', '--format', 'json', '--out', out_dir])
            assert result == 0
            captured = capsys.readouterr()
            output = json.loads(captured.out)

            # Verify broker_db key has expected fields
            assert 'brokers' in output['broker_db']
            assert 'verified' in output['broker_db']
            assert isinstance(output['broker_db']['brokers'], int)

    def test_json_exposures_key_is_list(self, capsys):
        with tempfile.TemporaryDirectory() as out_dir:
            result = main(['examples/sample.csv', '--format', 'json', '--out', out_dir])
            assert result == 0
            captured = capsys.readouterr()
            output = json.loads(captured.out)

            # Verify exposures is a list with entries
            assert isinstance(output['exposures'], list)
            assert len(output['exposures']) > 0

    def test_json_exposure_entry_structure(self, capsys):
        with tempfile.TemporaryDirectory() as out_dir:
            result = main(['examples/sample.csv', '--format', 'json', '--out', out_dir])
            assert result == 0
            captured = capsys.readouterr()
            output = json.loads(captured.out)

            # Verify each exposure has required fields
            for exposure in output['exposures']:
                assert 'id' in exposure
                assert 'name' in exposure
                assert 'location' in exposure
                assert 'sources' in exposure
                assert 'priority' in exposure
                assert 'deadname_matches' in exposure
                assert 'urls' in exposure

    def test_json_summary_key_structure(self, capsys):
        with tempfile.TemporaryDirectory() as out_dir:
            result = main(['examples/sample.csv', '--format', 'json', '--out', out_dir])
            assert result == 0
            captured = capsys.readouterr()
            output = json.loads(captured.out)

            # Verify summary has expected fields
            assert 'exposures' in output['summary']
            assert 'deduped_rows' in output['summary']
            assert 'high_priority' in output['summary']

    def test_json_requests_key_structure(self, capsys):
        with tempfile.TemporaryDirectory() as out_dir:
            result = main(['examples/sample.csv', '--format', 'json', '--out', out_dir])
            assert result == 0
            captured = capsys.readouterr()
            output = json.loads(captured.out)

            # Verify requests is a list
            assert isinstance(output['requests'], list)
            if output['requests']:
                for req in output['requests']:
                    assert 'broker' in req
                    assert 'slug' in req
                    assert 'file' in req

    def test_json_tracker_key_structure(self, capsys):
        with tempfile.TemporaryDirectory() as out_dir:
            result = main(['examples/sample.csv', '--format', 'json', '--out', out_dir])
            assert result == 0
            captured = capsys.readouterr()
            output = json.loads(captured.out)

            # Verify tracker has expected fields
            assert 'path' in output['tracker']
            assert 'pending' in output['tracker']
            assert 'submitted' in output['tracker']
            assert 'confirmed' in output['tracker']


class TestTextFormat:
    def test_format_text_on_sample_csv(self, capsys):
        with tempfile.TemporaryDirectory() as out_dir:
            result = main(['examples/sample.csv', '--format', 'text', '--out', out_dir])
            assert result == 0
            captured = capsys.readouterr()
            output = captured.out

            # Verify output is a string
            assert isinstance(output, str)
            assert len(output) > 0

    def test_text_format_contains_header(self, capsys):
        with tempfile.TemporaryDirectory() as out_dir:
            result = main(['examples/sample.csv', '--format', 'text', '--out', out_dir])
            assert result == 0
            captured = capsys.readouterr()

            # Verify human-readable header is present
            assert 'databroker-optout' in captured.out
            assert 'exposure audit' in captured.out

    def test_text_format_contains_input_info(self, capsys):
        with tempfile.TemporaryDirectory() as out_dir:
            result = main(['examples/sample.csv', '--format', 'text', '--out', out_dir])
            assert result == 0
            captured = capsys.readouterr()

            # Verify input section is present
            assert 'input:' in captured.out
            assert 'sample.csv' in captured.out

    def test_text_format_contains_broker_db_info(self, capsys):
        with tempfile.TemporaryDirectory() as out_dir:
            result = main(['examples/sample.csv', '--format', 'text', '--out', out_dir])
            assert result == 0
            captured = capsys.readouterr()

            # Verify broker DB info is present
            assert 'broker DB:' in captured.out
            assert 'brokers' in captured.out
            assert 'verified' in captured.out

    def test_text_format_contains_exposures_section(self, capsys):
        with tempfile.TemporaryDirectory() as out_dir:
            result = main(['examples/sample.csv', '--format', 'text', '--out', out_dir])
            assert result == 0
            captured = capsys.readouterr()

            # Verify exposures section is present
            assert 'exposures:' in captured.out
            assert 'unique' in captured.out

    def test_text_format_contains_tracker_section(self, capsys):
        with tempfile.TemporaryDirectory() as out_dir:
            result = main(['examples/sample.csv', '--format', 'text', '--out', out_dir])
            assert result == 0
            captured = capsys.readouterr()

            # Verify tracker section is present
            assert 'tracker:' in captured.out

    def test_text_format_default_without_flag(self, capsys):
        with tempfile.TemporaryDirectory() as out_dir:
            result = main(['examples/sample.csv', '--out', out_dir])
            assert result == 0
            captured = capsys.readouterr()

            # Default format should be text (human-readable)
            assert 'databroker-optout' in captured.out
            assert 'exposure audit' in captured.out
            assert 'exposures:' in captured.out
            assert 'tracker:' in captured.out


class TestJsonVsTextFormat:
    def test_json_and_text_have_different_output(self, capsys):
        with tempfile.TemporaryDirectory() as out_dir:
            # Run with JSON format
            main(['examples/sample.csv', '--format', 'json', '--out', out_dir])
            json_captured = capsys.readouterr()

            # Run with text format
            main(['examples/sample.csv', '--format', 'text', '--out', out_dir])
            text_captured = capsys.readouterr()

            # Verify they're different formats
            assert json_captured.out != text_captured.out

            # JSON should be parseable as JSON
            json.loads(json_captured.out)

            # Text should contain human-readable labels
            assert 'exposure audit' in text_captured.out
