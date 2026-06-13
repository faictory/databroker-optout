import subprocess
import os
import shutil


class TestE2EMakeRun:
    """End-to-end test of make run on bundled fixtures."""

    def test_make_run_exit_code_0(self):
        """The make run command should exit with code 0."""
        result = subprocess.run(
            ['make', 'run'],
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0

    def test_make_run_high_priority_marker(self):
        """The make run output should contain 'high priority: 1'."""
        result = subprocess.run(
            ['make', 'run'],
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert 'high priority: 1' in result.stdout

    def test_make_run_removal_requests_marker(self):
        """The make run output should contain 'removal requests: 5 written'."""
        result = subprocess.run(
            ['make', 'run'],
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert 'removal requests: 5 written' in result.stdout

    def test_make_run_tracker_marker(self):
        """The make run output should contain a non-empty tracker: line."""
        result = subprocess.run(
            ['make', 'run'],
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        # Verify the tracker line is present and non-empty
        output_lines = result.stdout.split('\n')
        tracker_lines = [line for line in output_lines if line.startswith('tracker:')]
        assert len(tracker_lines) > 0
        assert len(tracker_lines[0]) > len('tracker:')

    @classmethod
    def teardown_class(cls):
        """Clean up the brk-out directory after all tests."""
        brk_out = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'brk-out'
        )
        if os.path.exists(brk_out):
            shutil.rmtree(brk_out)
