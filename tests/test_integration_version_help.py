import subprocess
import sys
from databroker_optout import __version__
from databroker_optout.brokerdb import verified_date


class TestVersionIntegration:
    def test_version_flag_prints_version(self):
        result = subprocess.run(
            [sys.executable, '-m', 'databroker_optout', '--version'],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert __version__ in result.stdout

    def test_version_flag_prints_broker_db_date(self):
        result = subprocess.run(
            [sys.executable, '-m', 'databroker_optout', '--version'],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert verified_date() in result.stdout

    def test_version_flag_exits_0(self):
        result = subprocess.run(
            [sys.executable, '-m', 'databroker_optout', '--version'],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0


class TestHelpIntegration:
    def test_help_flag_lists_positional_input(self):
        result = subprocess.run(
            [sys.executable, '-m', 'databroker_optout', '--help'],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert 'input' in result.stdout.lower()

    def test_help_flag_lists_config_flag(self):
        result = subprocess.run(
            [sys.executable, '-m', 'databroker_optout', '--help'],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert '--config' in result.stdout

    def test_help_flag_lists_deadname_flag(self):
        result = subprocess.run(
            [sys.executable, '-m', 'databroker_optout', '--help'],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert '--deadname' in result.stdout

    def test_help_flag_lists_out_flag(self):
        result = subprocess.run(
            [sys.executable, '-m', 'databroker_optout', '--help'],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert '--out' in result.stdout

    def test_help_flag_lists_format_flag(self):
        result = subprocess.run(
            [sys.executable, '-m', 'databroker_optout', '--help'],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert '--format' in result.stdout

    def test_help_flag_lists_mark_flag(self):
        result = subprocess.run(
            [sys.executable, '-m', 'databroker_optout', '--help'],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert '--mark' in result.stdout

    def test_help_flag_lists_version_flag(self):
        result = subprocess.run(
            [sys.executable, '-m', 'databroker_optout', '--help'],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert '--version' in result.stdout

    def test_help_flag_lists_help_flag(self):
        result = subprocess.run(
            [sys.executable, '-m', 'databroker_optout', '--help'],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert '--help' in result.stdout

    def test_help_flag_exits_0(self):
        result = subprocess.run(
            [sys.executable, '-m', 'databroker_optout', '--help'],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0

    def test_h_flag_lists_positional_input(self):
        result = subprocess.run(
            [sys.executable, '-m', 'databroker_optout', '-h'],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert 'input' in result.stdout.lower()

    def test_h_flag_lists_config_flag(self):
        result = subprocess.run(
            [sys.executable, '-m', 'databroker_optout', '-h'],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert '--config' in result.stdout

    def test_h_flag_lists_deadname_flag(self):
        result = subprocess.run(
            [sys.executable, '-m', 'databroker_optout', '-h'],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert '--deadname' in result.stdout

    def test_h_flag_lists_out_flag(self):
        result = subprocess.run(
            [sys.executable, '-m', 'databroker_optout', '-h'],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert '--out' in result.stdout

    def test_h_flag_lists_format_flag(self):
        result = subprocess.run(
            [sys.executable, '-m', 'databroker_optout', '-h'],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert '--format' in result.stdout

    def test_h_flag_lists_mark_flag(self):
        result = subprocess.run(
            [sys.executable, '-m', 'databroker_optout', '-h'],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert '--mark' in result.stdout

    def test_h_flag_lists_version_flag(self):
        result = subprocess.run(
            [sys.executable, '-m', 'databroker_optout', '-h'],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert '--version' in result.stdout

    def test_h_flag_lists_help_flag(self):
        result = subprocess.run(
            [sys.executable, '-m', 'databroker_optout', '-h'],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert '--help' in result.stdout

    def test_h_flag_exits_0(self):
        result = subprocess.run(
            [sys.executable, '-m', 'databroker_optout', '-h'],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
