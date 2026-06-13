import os
import json
from databroker_optout.cli import main


class TestIntegrationOutFlag:
    def test_out_flag_redirects_output_and_prevents_default_dir(self, tmp_path):
        """Test that --out redirects output and prevents creation of default brk-out/ dir."""
        # Create a custom output directory
        out_dir = tmp_path / "custom_output"

        # Run CLI with --out flag
        result = main(['examples/sample.csv', '--out', str(out_dir)])
        assert result == 0

        # Verify files exist in the specified directory
        assert (out_dir / 'requests').exists()
        assert (out_dir / 'tracker.json').exists()

        # Verify requests directory has files
        requests_files = list((out_dir / 'requests').glob('*.txt'))
        assert len(requests_files) > 0

        # Verify tracker.json is valid
        with open(out_dir / 'tracker.json') as f:
            tracker = json.load(f)
        assert tracker['version'] == 1
        assert 'brokers' in tracker

        # Verify default brk-out/ directory was NOT created in cwd
        assert not os.path.exists('brk-out'), "Default brk-out/ directory should not be created when using --out flag"

    def test_out_flag_with_nested_directory(self, tmp_path):
        """Test that --out works with nested directory paths."""
        out_dir = tmp_path / "nested" / "output" / "dir"

        result = main(['examples/sample.csv', '--out', str(out_dir)])
        assert result == 0

        # Verify all files are in the nested directory
        assert (out_dir / 'requests').exists()
        assert (out_dir / 'tracker.json').exists()
        assert not os.path.exists('brk-out'), "Default brk-out/ directory should not exist"

    def test_out_flag_prevents_default_dir_with_multiple_runs(self, tmp_path):
        """Test that --out prevents default dir creation across multiple runs."""
        out_dir1 = tmp_path / "output1"
        out_dir2 = tmp_path / "output2"

        # First run
        result1 = main(['examples/sample.csv', '--out', str(out_dir1)])
        assert result1 == 0
        assert (out_dir1 / 'tracker.json').exists()
        assert not os.path.exists('brk-out')

        # Second run
        result2 = main(['examples/sample.csv', '--out', str(out_dir2)])
        assert result2 == 0
        assert (out_dir2 / 'tracker.json').exists()
        assert not os.path.exists('brk-out'), "Default brk-out/ should not exist after multiple runs with --out"
