import subprocess
import os
import shutil
import json


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

    def test_make_run_creates_requests_files(self):
        """The make run command should create request files in brk-out/requests/."""
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        result = subprocess.run(
            ['make', 'run'],
            cwd=project_root,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0

        requests_dir = os.path.join(project_root, 'brk-out', 'requests')
        assert os.path.isdir(requests_dir), f"requests directory {requests_dir} should exist"

        # Verify request files were created
        request_files = [f for f in os.listdir(requests_dir) if f.endswith('.txt')]
        assert len(request_files) > 0, "At least one request file should be created"
        assert len(request_files) == 5, "Expected 5 request files for sample.csv"

        # Verify each file has content
        for filename in request_files:
            file_path = os.path.join(requests_dir, filename)
            with open(file_path, 'r') as f:
                content = f.read()
                assert len(content) > 0, f"Request file {filename} should have content"

    def test_make_run_creates_tracker_json(self):
        """The make run command should create tracker.json with correct structure."""
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        result = subprocess.run(
            ['make', 'run'],
            cwd=project_root,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0

        tracker_path = os.path.join(project_root, 'brk-out', 'tracker.json')
        assert os.path.isfile(tracker_path), f"tracker.json should exist at {tracker_path}"

        # Load and verify tracker.json structure
        with open(tracker_path, 'r') as f:
            tracker = json.load(f)

        # Verify top-level structure
        assert 'version' in tracker, "tracker.json should have 'version' key"
        assert 'updated' in tracker, "tracker.json should have 'updated' key"
        assert 'brokers' in tracker, "tracker.json should have 'brokers' key"

        brokers = tracker['brokers']
        assert isinstance(brokers, dict), "brokers should be a dictionary"
        assert len(brokers) > 0, "brokers should have entries"
        assert len(brokers) == 5, "Expected 5 brokers for sample.csv"

        # Verify each broker entry has required fields
        for slug, broker_info in brokers.items():
            assert 'broker' in broker_info, f"Broker entry {slug} should have 'broker' field"
            assert 'status' in broker_info, f"Broker entry {slug} should have 'status' field"
            assert 'exposure_ids' in broker_info, f"Broker entry {slug} should have 'exposure_ids' field"
            assert 'request_file' in broker_info, f"Broker entry {slug} should have 'request_file' field"
            assert 'history' in broker_info, f"Broker entry {slug} should have 'history' field"

            # Verify status is valid
            assert broker_info['status'] in ('pending', 'submitted', 'confirmed'), \
                f"Broker {slug} status should be valid"

            # Verify exposure_ids is a list
            assert isinstance(broker_info['exposure_ids'], list), \
                f"Broker {slug} exposure_ids should be a list"
            assert len(broker_info['exposure_ids']) > 0, \
                f"Broker {slug} should have at least one exposure"

            # Verify history is a list with at least one entry
            assert isinstance(broker_info['history'], list), \
                f"Broker {slug} history should be a list"
            assert len(broker_info['history']) > 0, \
                f"Broker {slug} history should have at least one entry"

    @classmethod
    def teardown_class(cls):
        """Clean up the brk-out directory after all tests."""
        brk_out = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'brk-out'
        )
        if os.path.exists(brk_out):
            shutil.rmtree(brk_out)
