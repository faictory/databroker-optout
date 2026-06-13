import sys
import subprocess


class TestE2EMalformedInput:
    def test_malformed_input_rejection_via_subprocess(self):
        result = subprocess.run(
            [sys.executable, '-m', 'broker_removal_kit', 'examples/bad-missing-name.csv'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 2
        assert 'error:' in result.stderr
        assert 'name' in result.stderr
