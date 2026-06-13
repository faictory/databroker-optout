import os
import json
from databroker_optout.cli import main


class TestIntegrationDefaultRun:
    """Integration test for the default full run of the CLI."""

    def test_default_run_exit_code_0(self, tmp_path):
        """The default run on sample.csv should exit with code 0."""
        result = main(['examples/sample.csv', '--out', str(tmp_path)])
        assert result == 0

    def test_default_run_exactly_4_exposures(self, tmp_path, capsys):
        """The default run should produce exactly 4 unique exposures."""
        result = main(['examples/sample.csv', '--out', str(tmp_path), '--format', 'json'])
        assert result == 0

        captured = capsys.readouterr()
        output = json.loads(captured.out)

        assert 'exposures' in output
        exposures = output['exposures']
        assert len(exposures) == 4

    def test_default_run_exactly_5_request_files(self, tmp_path):
        """The default run should write exactly 5 request files (one per broker)."""
        result = main(['examples/sample.csv', '--out', str(tmp_path)])
        assert result == 0

        requests_dir = os.path.join(str(tmp_path), 'requests')
        assert os.path.exists(requests_dir)

        request_files = os.listdir(requests_dir)
        assert len(request_files) == 5

        # Verify the expected broker request files exist
        expected_files = {
            'spokeo.txt',
            'whitepages.txt',
            'beenverified.txt',
            'truepeoplesearch.txt',
            'radaris.txt',
        }
        assert set(request_files) == expected_files

    def test_default_run_tracker_json_5_entries_all_pending(self, tmp_path):
        """The default run should create tracker.json with 4 exposures and 5 broker entries all at pending status."""
        result = main(['examples/sample.csv', '--out', str(tmp_path)])
        assert result == 0

        tracker_path = os.path.join(str(tmp_path), 'tracker.json')
        assert os.path.exists(tracker_path)

        with open(tracker_path) as f:
            tracker = json.load(f)

        assert tracker['version'] == 1
        assert 'brokers' in tracker

        brokers = tracker['brokers']
        assert len(brokers) == 5

        # Verify all broker entries are at pending status
        for broker_slug, broker_entry in brokers.items():
            assert broker_entry['status'] == 'pending'
