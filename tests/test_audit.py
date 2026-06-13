import os
import json
import tempfile
from broker_removal_kit.audit import run_audit


class TestRunAudit:
    def test_run_audit_basic_fixture(self):
        """Test run_audit on the six-row fixture produces correct exposure count and request files."""
        with tempfile.TemporaryDirectory() as out_dir:
            result = run_audit(
                'examples/sample.csv',
                identity=None,
                deadnames=[],
                out_dir=out_dir,
                marks=[],
                now='2026-06-12T17:30:00Z'
            )

            # Check result shape
            assert 'input' in result
            assert 'broker_db' in result
            assert 'exposures' in result
            assert 'summary' in result
            assert 'requests' in result
            assert 'tracker' in result

            # Check summary counts
            assert result['summary']['exposures'] == 4
            assert result['summary']['deduped_rows'] == 2
            assert result['summary']['high_priority'] == 0

            # Check request files count
            assert len(result['requests']) == 5

            # Verify request files exist
            requests_dir = os.path.join(out_dir, 'requests')
            assert os.path.exists(requests_dir)
            request_files = os.listdir(requests_dir)
            assert len(request_files) == 5

            # Check request files
            expected_slugs = {'spokeo', 'whitepages', 'beenverified', 'truepeoplesearch', 'radaris'}
            actual_slugs = {f.replace('.txt', '') for f in request_files}
            assert actual_slugs == expected_slugs

            # Verify tracker.json exists
            tracker_path = os.path.join(out_dir, 'tracker.json')
            assert os.path.exists(tracker_path)

            with open(tracker_path, 'r') as f:
                tracker_data = json.load(f)

            assert tracker_data['version'] == 1
            assert len(tracker_data['brokers']) == 5
            for broker_info in tracker_data['brokers'].values():
                assert broker_info['status'] == 'pending'

    def test_run_audit_with_identity(self):
        """Test that requester identity is filled in request signatures."""
        with tempfile.TemporaryDirectory() as out_dir:
            identity = {
                'name': 'Jordan Rivera',
                'email': 'jordan@example.com',
                'address': 'PO Box 1234, Portland, OR 97201',
            }

            run_audit(
                'examples/sample.csv',
                identity=identity,
                deadnames=[],
                out_dir=out_dir,
                marks=[],
                now='2026-06-12T17:30:00Z'
            )

            # Check that identity is in request files
            requests_dir = os.path.join(out_dir, 'requests')
            spokeo_file = os.path.join(requests_dir, 'spokeo.txt')
            with open(spokeo_file, 'r') as f:
                content = f.read()

            assert 'Jordan Rivera' in content
            assert 'jordan@example.com' in content
            assert 'PO Box 1234, Portland, OR 97201' in content

    def test_run_audit_with_deadnames(self):
        """Test that deadname matching marks exposures as high priority."""
        with tempfile.TemporaryDirectory() as out_dir:
            result = run_audit(
                'examples/sample.csv',
                identity=None,
                deadnames=['James Rivera'],
                out_dir=out_dir,
                marks=[],
                now='2026-06-12T17:30:00Z'
            )

            # Check that one exposure is marked high priority
            assert result['summary']['high_priority'] == 1

            # Check that the high priority exposure has deadname matches
            high_priority_exposures = [e for e in result['exposures'] if e['priority'] == 'high']
            assert len(high_priority_exposures) == 1
            assert 'James Rivera' in high_priority_exposures[0]['deadname_matches']

    def test_run_audit_with_mark(self):
        """Test that --mark transitions broker status correctly."""
        with tempfile.TemporaryDirectory() as out_dir:
            marks = [{'broker': 'spokeo', 'status': 'submitted'}]

            result = run_audit(
                'examples/sample.csv',
                identity=None,
                deadnames=[],
                out_dir=out_dir,
                marks=marks,
                now='2026-06-12T17:30:00Z'
            )

            # Check tracker counts
            assert result['tracker']['pending'] == 4
            assert result['tracker']['submitted'] == 1
            assert result['tracker']['confirmed'] == 0

            # Verify in tracker.json
            tracker_path = os.path.join(out_dir, 'tracker.json')
            with open(tracker_path, 'r') as f:
                tracker_data = json.load(f)

            assert tracker_data['brokers']['spokeo']['status'] == 'submitted'

    def test_run_audit_input_info(self):
        """Test that input info is correctly captured."""
        with tempfile.TemporaryDirectory() as out_dir:
            result = run_audit(
                'examples/sample.csv',
                identity=None,
                deadnames=[],
                out_dir=out_dir,
                marks=[],
                now='2026-06-12T17:30:00Z'
            )

            assert result['input']['path'] == 'examples/sample.csv'
            assert result['input']['rows'] == 6
            assert result['input']['format'] == 'csv'

    def test_run_audit_broker_db_info(self):
        """Test that broker DB info is correctly captured."""
        with tempfile.TemporaryDirectory() as out_dir:
            result = run_audit(
                'examples/sample.csv',
                identity=None,
                deadnames=[],
                out_dir=out_dir,
                marks=[],
                now='2026-06-12T17:30:00Z'
            )

            assert result['broker_db']['brokers'] >= 12
            assert result['broker_db']['verified'] == '2026-01-15'

    def test_run_audit_exposures_structure(self):
        """Test that exposures have the expected structure."""
        with tempfile.TemporaryDirectory() as out_dir:
            result = run_audit(
                'examples/sample.csv',
                identity=None,
                deadnames=[],
                out_dir=out_dir,
                marks=[],
                now='2026-06-12T17:30:00Z'
            )

            for exposure in result['exposures']:
                assert 'id' in exposure
                assert 'name' in exposure
                assert 'location' in exposure
                assert 'sources' in exposure
                assert 'priority' in exposure
                assert 'deadname_matches' in exposure

    def test_run_audit_requests_structure(self):
        """Test that requests have the expected structure."""
        with tempfile.TemporaryDirectory() as out_dir:
            result = run_audit(
                'examples/sample.csv',
                identity=None,
                deadnames=[],
                out_dir=out_dir,
                marks=[],
                now='2026-06-12T17:30:00Z'
            )

            for request in result['requests']:
                assert 'broker' in request
                assert 'slug' in request
                assert 'file' in request
                assert request['file'].startswith('requests/')
                assert request['file'].endswith('.txt')

    def test_run_audit_tracker_info(self):
        """Test that tracker info is correctly captured."""
        with tempfile.TemporaryDirectory() as out_dir:
            result = run_audit(
                'examples/sample.csv',
                identity=None,
                deadnames=[],
                out_dir=out_dir,
                marks=[],
                now='2026-06-12T17:30:00Z'
            )

            assert 'path' in result['tracker']
            assert 'pending' in result['tracker']
            assert 'submitted' in result['tracker']
            assert 'confirmed' in result['tracker']
            assert result['tracker']['path'].endswith('tracker.json')

    def test_run_audit_with_identity_and_deadnames(self):
        """Test combined identity and deadnames."""
        with tempfile.TemporaryDirectory() as out_dir:
            identity = {
                'name': 'Jordan Rivera',
                'email': 'jordan@example.com',
                'address': 'PO Box 1234, Portland, OR 97201',
            }

            result = run_audit(
                'examples/sample.csv',
                identity=identity,
                deadnames=['James Rivera'],
                out_dir=out_dir,
                marks=[],
                now='2026-06-12T17:30:00Z'
            )

            # Check high priority
            assert result['summary']['high_priority'] == 1

            # Check request file has identity
            requests_dir = os.path.join(out_dir, 'requests')
            spokeo_file = os.path.join(requests_dir, 'spokeo.txt')
            with open(spokeo_file, 'r') as f:
                content = f.read()

            assert 'Jordan Rivera' in content
            assert 'deadname' not in content.lower() or 'James' not in content  # deadname not in the request itself

    def test_run_audit_multiple_marks(self):
        """Test multiple mark transitions."""
        with tempfile.TemporaryDirectory() as out_dir:
            marks = [
                {'broker': 'spokeo', 'status': 'submitted'},
                {'broker': 'whitepages', 'status': 'confirmed'},
            ]

            result = run_audit(
                'examples/sample.csv',
                identity=None,
                deadnames=[],
                out_dir=out_dir,
                marks=marks,
                now='2026-06-12T17:30:00Z'
            )

            # Check tracker counts
            assert result['tracker']['pending'] == 3
            assert result['tracker']['submitted'] == 1
            assert result['tracker']['confirmed'] == 1

            # Verify in tracker.json
            tracker_path = os.path.join(out_dir, 'tracker.json')
            with open(tracker_path, 'r') as f:
                tracker_data = json.load(f)

            assert tracker_data['brokers']['spokeo']['status'] == 'submitted'
            assert tracker_data['brokers']['whitepages']['status'] == 'confirmed'
