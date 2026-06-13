import os
import sys
import json
import tempfile
from databroker_optout.cli import main
from databroker_optout import __version__


class TestVersion:
    def test_version_flag_prints_version_and_date(self, capsys):
        result = main(['--version'])
        assert result == 0
        captured = capsys.readouterr()
        assert __version__ in captured.out
        assert 'broker DB verified' in captured.out

    def test_version_flag_exits_0(self):
        result = main(['--version'])
        assert result == 0


class TestHelp:
    def test_help_flag_prints_help(self, capsys):
        result = main(['--help'])
        assert result == 0
        captured = capsys.readouterr()
        assert 'databroker-optout' in captured.out or 'usage' in captured.out

    def test_h_flag_prints_help(self, capsys):
        result = main(['-h'])
        assert result == 0
        captured = capsys.readouterr()
        assert 'databroker-optout' in captured.out or 'usage' in captured.out


class TestBasicRun:
    def test_default_run_on_fixture_exits_0(self):
        with tempfile.TemporaryDirectory() as out_dir:
            result = main(['examples/sample.csv', '--out', out_dir])
            assert result == 0

    def test_default_run_prints_text_summary(self, capsys):
        with tempfile.TemporaryDirectory() as out_dir:
            result = main(['examples/sample.csv', '--out', out_dir])
            assert result == 0
            captured = capsys.readouterr()
            assert 'databroker-optout' in captured.out
            assert 'exposures' in captured.out

    def test_default_run_writes_requests(self):
        with tempfile.TemporaryDirectory() as out_dir:
            result = main(['examples/sample.csv', '--out', out_dir])
            assert result == 0
            requests_dir = os.path.join(out_dir, 'requests')
            assert os.path.exists(requests_dir)
            assert len(os.listdir(requests_dir)) > 0

    def test_default_run_writes_tracker(self):
        with tempfile.TemporaryDirectory() as out_dir:
            result = main(['examples/sample.csv', '--out', out_dir])
            assert result == 0
            tracker_path = os.path.join(out_dir, 'tracker.json')
            assert os.path.exists(tracker_path)
            with open(tracker_path) as f:
                tracker = json.load(f)
            assert tracker['version'] == 1
            assert 'brokers' in tracker


class TestFormatFlag:
    def test_format_json_prints_json(self, capsys):
        with tempfile.TemporaryDirectory() as out_dir:
            result = main(['examples/sample.csv', '--out', out_dir, '--format', 'json'])
            assert result == 0
            captured = capsys.readouterr()
            output = json.loads(captured.out)
            assert 'input' in output
            assert 'exposures' in output
            assert 'summary' in output
            assert 'requests' in output
            assert 'tracker' in output

    def test_format_json_is_valid_json(self, capsys):
        with tempfile.TemporaryDirectory() as out_dir:
            result = main(['examples/sample.csv', '--out', out_dir, '--format', 'json'])
            assert result == 0
            captured = capsys.readouterr()
            json.loads(captured.out)

    def test_format_text_default(self, capsys):
        with tempfile.TemporaryDirectory() as out_dir:
            result = main(['examples/sample.csv', '--out', out_dir])
            assert result == 0
            captured = capsys.readouterr()
            assert 'exposures:' in captured.out or 'exposures' in captured.out


class TestDeadnameFlag:
    def test_deadname_flags_exposure_high(self, capsys):
        with tempfile.TemporaryDirectory() as out_dir:
            result = main(['examples/sample.csv', '--out', out_dir, '--deadname', 'James Rivera'])
            assert result == 0
            captured = capsys.readouterr()
            assert 'HIGH' in captured.out or 'high' in captured.out

    def test_multiple_deadnames(self, capsys):
        with tempfile.TemporaryDirectory() as out_dir:
            result = main([
                'examples/sample.csv',
                '--out', out_dir,
                '--deadname', 'James Rivera',
                '--deadname', 'Kim Brown'
            ])
            assert result == 0

    def test_deadname_json_format(self, capsys):
        with tempfile.TemporaryDirectory() as out_dir:
            result = main([
                'examples/sample.csv',
                '--out', out_dir,
                '--deadname', 'James Rivera',
                '--format', 'json'
            ])
            assert result == 0
            captured = capsys.readouterr()
            output = json.loads(captured.out)
            assert any(exp.get('priority') == 'high' for exp in output.get('exposures', []))


class TestConfigFlag:
    def test_config_loads_identity_and_deadnames(self, capsys):
        with tempfile.TemporaryDirectory() as out_dir:
            result = main(['examples/sample.csv', '--config', 'examples/brk.toml', '--out', out_dir])
            assert result == 0
            captured = capsys.readouterr()
            assert 'HIGH' in captured.out or 'high' in captured.out

    def test_config_identity_in_request(self):
        with tempfile.TemporaryDirectory() as out_dir:
            result = main(['examples/sample.csv', '--config', 'examples/brk.toml', '--out', out_dir])
            assert result == 0
            requests_dir = os.path.join(out_dir, 'requests')
            request_file = os.path.join(requests_dir, 'spokeo.txt')
            with open(request_file) as f:
                content = f.read()
            assert 'Jordan Rivera' in content
            assert 'jordan@example.com' in content

    def test_config_not_found_exits_2(self, capsys):
        result = main(['examples/sample.csv', '--config', '/nonexistent/config.toml'])
        assert result == 2
        captured = capsys.readouterr()
        assert 'error' in captured.err

    def test_partial_config_uses_placeholders(self):
        with tempfile.TemporaryDirectory() as out_dir:
            config_path = os.path.join(out_dir, 'partial.toml')
            with open(config_path, 'w') as f:
                f.write('name = "Alex Smith"\n')
                f.write('email = "alex@example.com"\n')

            result = main(['examples/sample.csv', '--config', config_path, '--out', out_dir])
            assert result == 0
            requests_dir = os.path.join(out_dir, 'requests')
            request_file = os.path.join(requests_dir, 'spokeo.txt')
            with open(request_file) as f:
                content = f.read()
            assert 'Alex Smith' in content
            assert 'alex@example.com' in content
            assert '<YOUR ADDRESS>' in content


class TestOutFlag:
    def test_out_creates_directory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            out_dir = os.path.join(tmpdir, 'custom-out')
            result = main(['examples/sample.csv', '--out', out_dir])
            assert result == 0
            assert os.path.exists(out_dir)
            assert os.path.exists(os.path.join(out_dir, 'requests'))
            assert os.path.exists(os.path.join(out_dir, 'tracker.json'))

    def test_out_override_explicit_brk_out(self):
        """Test that explicit --out brk-out overrides config dir."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, 'config.toml')
            with open(config_path, 'w') as f:
                f.write('name = "Test"\n')
                f.write(f'dir = "{tmpdir}/config-dir"\n')

            out_dir = os.path.join(tmpdir, 'brk-out')
            result = main([
                'examples/sample.csv',
                '--config', config_path,
                '--out', out_dir
            ])
            assert result == 0
            tracker_path = os.path.join(out_dir, 'tracker.json')
            assert os.path.exists(tracker_path)

    def test_out_config_default(self):
        """Test that config dir is used when --out is not specified."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = os.path.join(tmpdir, 'config-dir')
            os.makedirs(config_dir, exist_ok=True)

            config_path = os.path.join(tmpdir, 'config.toml')
            with open(config_path, 'w') as f:
                f.write('name = "Test"\n')
                f.write(f'dir = "{config_dir}"\n')

            result = main([
                'examples/sample.csv',
                '--config', config_path
            ])
            assert result == 0
            tracker_path = os.path.join(config_dir, 'tracker.json')
            assert os.path.exists(tracker_path)


class TestMarkFlag:
    def test_mark_transitions_status(self):
        with tempfile.TemporaryDirectory() as out_dir:
            result = main(['examples/sample.csv', '--out', out_dir, '--mark', 'spokeo=submitted'])
            assert result == 0
            tracker_path = os.path.join(out_dir, 'tracker.json')
            with open(tracker_path) as f:
                tracker = json.load(f)
            assert tracker['brokers']['spokeo']['status'] == 'submitted'

    def test_mark_persists_on_rerun(self):
        with tempfile.TemporaryDirectory() as out_dir:
            main(['examples/sample.csv', '--out', out_dir, '--mark', 'spokeo=submitted'])
            result = main(['examples/sample.csv', '--out', out_dir])
            assert result == 0
            tracker_path = os.path.join(out_dir, 'tracker.json')
            with open(tracker_path) as f:
                tracker = json.load(f)
            assert tracker['brokers']['spokeo']['status'] == 'submitted'

    def test_multiple_marks(self):
        with tempfile.TemporaryDirectory() as out_dir:
            result = main([
                'examples/sample.csv', '--out', out_dir,
                '--mark', 'spokeo=submitted',
                '--mark', 'whitepages=confirmed'
            ])
            assert result == 0
            tracker_path = os.path.join(out_dir, 'tracker.json')
            with open(tracker_path) as f:
                tracker = json.load(f)
            assert tracker['brokers']['spokeo']['status'] == 'submitted'
            assert tracker['brokers']['whitepages']['status'] == 'confirmed'


class TestErrors:
    def test_missing_input_exits_2(self, capsys):
        result = main([])
        assert result == 2
        captured = capsys.readouterr()
        assert 'error' in captured.err

    def test_missing_required_column_exits_2(self, capsys):
        result = main(['examples/bad-missing-name.csv'])
        assert result == 2
        captured = capsys.readouterr()
        assert 'error' in captured.err
        assert 'name' in captured.err

    def test_nonexistent_input_exits_2(self, capsys):
        result = main(['/nonexistent/file.csv'])
        assert result == 2
        captured = capsys.readouterr()
        assert 'error' in captured.err

    def test_bad_mark_format_exits_2(self, capsys):
        result = main(['examples/sample.csv', '--mark', 'invalid-format'])
        assert result == 2
        captured = capsys.readouterr()
        assert 'error' in captured.err

    def test_invalid_status_exits_2(self, capsys):
        result = main(['examples/sample.csv', '--mark', 'spokeo=invalid-status'])
        assert result == 2
        captured = capsys.readouterr()
        assert 'error' in captured.err


class TestJsonInput:
    def test_json_input_file(self):
        with tempfile.TemporaryDirectory() as out_dir:
            result = main(['examples/sample.json', '--out', out_dir])
            assert result == 0

    def test_json_input_format_json_output(self, capsys):
        with tempfile.TemporaryDirectory() as out_dir:
            result = main(['examples/sample.json', '--out', out_dir, '--format', 'json'])
            assert result == 0
            captured = capsys.readouterr()
            output = json.loads(captured.out)
            assert output['input']['format'] == 'json'


class TestMainModule:
    def test_main_module_invocation(self):
        import subprocess
        result = subprocess.run(
            [sys.executable, '-m', 'databroker_optout', '--version'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert 'broker DB verified' in result.stdout
