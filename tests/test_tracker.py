import json
import os
import pytest
import tempfile
from broker_removal_kit.tracker import parse_mark, reconcile
from broker_removal_kit.errors import BrokerKitError


class TestParseMark:
    def test_parse_mark_happy_path_pending(self):
        result = parse_mark('spokeo=pending')
        assert result == {'broker': 'spokeo', 'status': 'pending'}

    def test_parse_mark_happy_path_submitted(self):
        result = parse_mark('whitepages=submitted')
        assert result == {'broker': 'whitepages', 'status': 'submitted'}

    def test_parse_mark_happy_path_confirmed(self):
        result = parse_mark('spokeo=confirmed')
        assert result == {'broker': 'spokeo', 'status': 'confirmed'}

    def test_parse_mark_with_spaces(self):
        result = parse_mark('  spokeo  =  pending  ')
        assert result == {'broker': 'spokeo', 'status': 'pending'}

    def test_parse_mark_missing_equals_raises_brokerkiterror(self):
        with pytest.raises(BrokerKitError, match="invalid mark format"):
            parse_mark('spokeo-pending')

    def test_parse_mark_missing_equals_no_value_raises_brokerkiterror(self):
        with pytest.raises(BrokerKitError, match="invalid mark format"):
            parse_mark('spokeo')

    def test_parse_mark_invalid_status_raises_brokerkiterror(self):
        with pytest.raises(BrokerKitError, match="invalid status"):
            parse_mark('spokeo=invalid')

    def test_parse_mark_invalid_status_misspelled_raises_brokerkiterror(self):
        with pytest.raises(BrokerKitError, match="invalid status"):
            parse_mark('spokeo=pend')

    def test_parse_mark_empty_status_raises_brokerkiterror(self):
        with pytest.raises(BrokerKitError, match="invalid status"):
            parse_mark('spokeo=')


class TestReconcile:
    def test_reconcile_first_run_creates_tracker_with_all_pending(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tracker_path = os.path.join(tmpdir, 'tracker.json')
            brokers = {
                'spokeo': {'name': 'Spokeo', 'opt_out_url': 'https://spokeo.com/optout', 'exposure_ids': ['exp-001']},
                'whitepages': {'name': 'WhitePages', 'opt_out_url': 'https://whitepages.com/optout', 'exposure_ids': ['exp-001']},
            }
            exposures = [
                {
                    'id': 'exp-001',
                    'name': 'Jordan Rivera',
                    'location': 'Portland, OR',
                    'aliases': ['James Rivera'],
                    'records': [
                        {'broker': 'Spokeo', 'url': 'https://spokeo.com/Jordan-Rivera', 'location': 'Portland, OR'},
                        {'broker': 'WhitePages', 'url': 'https://whitepages.com/name/Jordan-Rivera', 'location': 'Portland, OR'},
                    ]
                }
            ]
            marks = []
            now = '2026-06-12T17:30:00Z'

            counts = reconcile(tracker_path, exposures, brokers, marks, now)

            assert counts == {'pending': 2, 'submitted': 0, 'confirmed': 0}
            assert os.path.exists(tracker_path)

            with open(tracker_path, 'r') as f:
                data = json.load(f)

            assert data['version'] == 1
            assert data['updated'] == now
            assert len(data['exposures']) == 1
            assert 'exp-001' in data['exposures']
            assert data['exposures']['exp-001']['brokers']['spokeo']['status'] == 'pending'
            assert data['exposures']['exp-001']['brokers']['whitepages']['status'] == 'pending'
            assert data['exposures']['exp-001']['brokers']['spokeo']['history'] == [{'status': 'pending', 'at': now}]

    def test_reconcile_rerun_preserves_existing_status(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tracker_path = os.path.join(tmpdir, 'tracker.json')
            brokers = {
                'spokeo': {'name': 'Spokeo', 'opt_out_url': 'https://spokeo.com/optout', 'exposure_ids': ['exp-001']},
            }
            exposures = [
                {
                    'id': 'exp-001',
                    'name': 'Jordan Rivera',
                    'location': 'Portland, OR',
                    'aliases': [],
                    'records': [
                        {'broker': 'Spokeo', 'url': 'https://spokeo.com/Jordan-Rivera', 'location': 'Portland, OR'},
                    ]
                }
            ]

            first_now = '2026-06-12T17:30:00Z'
            reconcile(tracker_path, exposures, brokers, [], first_now)

            second_now = '2026-06-13T10:00:00Z'
            reconcile(tracker_path, exposures, brokers, [], second_now)

            with open(tracker_path, 'r') as f:
                data = json.load(f)

            assert data['exposures']['exp-001']['brokers']['spokeo']['status'] == 'pending'
            assert data['updated'] == second_now

    def test_reconcile_mark_transitions_status_and_appends_history(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tracker_path = os.path.join(tmpdir, 'tracker.json')
            brokers = {
                'spokeo': {'name': 'Spokeo', 'opt_out_url': 'https://spokeo.com/optout', 'exposure_ids': ['exp-001']},
            }
            exposures = [
                {
                    'id': 'exp-001',
                    'name': 'Jordan Rivera',
                    'location': 'Portland, OR',
                    'aliases': [],
                    'records': [
                        {'broker': 'Spokeo', 'url': 'https://spokeo.com/Jordan-Rivera', 'location': 'Portland, OR'},
                    ]
                }
            ]
            first_now = '2026-06-12T17:30:00Z'

            reconcile(tracker_path, exposures, brokers, [], first_now)

            second_marks = [{'broker': 'spokeo', 'status': 'submitted'}]
            second_now = '2026-06-13T10:00:00Z'
            counts = reconcile(tracker_path, exposures, brokers, second_marks, second_now)

            assert counts == {'pending': 0, 'submitted': 1, 'confirmed': 0}

            with open(tracker_path, 'r') as f:
                data = json.load(f)

            history = data['exposures']['exp-001']['brokers']['spokeo']['history']
            assert len(history) == 2
            assert history[0] == {'status': 'pending', 'at': first_now}
            assert history[1] == {'status': 'submitted', 'at': second_now}

    def test_reconcile_mark_persists_across_reruns(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tracker_path = os.path.join(tmpdir, 'tracker.json')
            brokers = {
                'spokeo': {'name': 'Spokeo', 'opt_out_url': 'https://spokeo.com/optout', 'exposure_ids': ['exp-001']},
            }
            exposures = [
                {
                    'id': 'exp-001',
                    'name': 'Jordan Rivera',
                    'location': 'Portland, OR',
                    'aliases': [],
                    'records': [
                        {'broker': 'Spokeo', 'url': 'https://spokeo.com/Jordan-Rivera', 'location': 'Portland, OR'},
                    ]
                }
            ]

            first_now = '2026-06-12T17:30:00Z'
            first_marks = [{'broker': 'spokeo', 'status': 'submitted'}]
            reconcile(tracker_path, exposures, brokers, first_marks, first_now)

            second_now = '2026-06-13T10:00:00Z'
            counts = reconcile(tracker_path, exposures, brokers, [], second_now)

            assert counts == {'pending': 0, 'submitted': 1, 'confirmed': 0}

            with open(tracker_path, 'r') as f:
                data = json.load(f)

            assert data['exposures']['exp-001']['brokers']['spokeo']['status'] == 'submitted'

    def test_reconcile_adds_new_brokers_on_rerun(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tracker_path = os.path.join(tmpdir, 'tracker.json')
            first_brokers = {
                'spokeo': {'name': 'Spokeo', 'opt_out_url': 'https://spokeo.com/optout', 'exposure_ids': ['exp-001']},
            }
            exposures_1 = [
                {
                    'id': 'exp-001',
                    'name': 'Jordan Rivera',
                    'location': 'Portland, OR',
                    'aliases': [],
                    'records': [
                        {'broker': 'Spokeo', 'url': 'https://spokeo.com/Jordan-Rivera', 'location': 'Portland, OR'},
                    ]
                }
            ]

            first_now = '2026-06-12T17:30:00Z'
            reconcile(tracker_path, exposures_1, first_brokers, [], first_now)

            second_brokers = {
                'spokeo': {'name': 'Spokeo', 'opt_out_url': 'https://spokeo.com/optout', 'exposure_ids': ['exp-001']},
                'whitepages': {'name': 'WhitePages', 'opt_out_url': 'https://whitepages.com/optout', 'exposure_ids': ['exp-001']},
            }
            exposures_2 = [
                {
                    'id': 'exp-001',
                    'name': 'Jordan Rivera',
                    'location': 'Portland, OR',
                    'aliases': [],
                    'records': [
                        {'broker': 'Spokeo', 'url': 'https://spokeo.com/Jordan-Rivera', 'location': 'Portland, OR'},
                        {'broker': 'WhitePages', 'url': 'https://whitepages.com/name/Jordan-Rivera', 'location': 'Portland, OR'},
                    ]
                }
            ]

            second_now = '2026-06-13T10:00:00Z'
            counts = reconcile(tracker_path, exposures_2, second_brokers, [], second_now)

            assert counts == {'pending': 2, 'submitted': 0, 'confirmed': 0}

            with open(tracker_path, 'r') as f:
                data = json.load(f)

            assert len(data['exposures']['exp-001']['brokers']) == 2
            assert 'spokeo' in data['exposures']['exp-001']['brokers']
            assert 'whitepages' in data['exposures']['exp-001']['brokers']

    def test_reconcile_sets_required_fields(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tracker_path = os.path.join(tmpdir, 'tracker.json')
            brokers = {
                'spokeo': {'name': 'Spokeo', 'opt_out_url': 'https://spokeo.com/optout', 'exposure_ids': ['exp-001', 'exp-002']},
            }
            exposures = [
                {
                    'id': 'exp-001',
                    'name': 'Jordan Rivera',
                    'location': 'Portland, OR',
                    'aliases': [],
                    'records': [
                        {'broker': 'Spokeo', 'url': 'https://spokeo.com/Jordan-Rivera', 'location': 'Portland, OR'},
                    ]
                },
                {
                    'id': 'exp-002',
                    'name': 'Jordan Rivera',
                    'location': 'Seattle, WA',
                    'aliases': [],
                    'records': [
                        {'broker': 'Spokeo', 'url': 'https://spokeo.com/Jordan-Rivera-2', 'location': 'Seattle, WA'},
                    ]
                }
            ]
            marks = []
            now = '2026-06-12T17:30:00Z'

            reconcile(tracker_path, exposures, brokers, marks, now)

            with open(tracker_path, 'r') as f:
                data = json.load(f)

            for exp_id in ['exp-001', 'exp-002']:
                broker_entry = data['exposures'][exp_id]['brokers']['spokeo']
                assert broker_entry['broker'] == 'Spokeo'
                assert broker_entry['request_file'] == 'requests/spokeo.txt'
                assert broker_entry['opt_out_url'] == 'https://spokeo.com/optout'
                assert broker_entry['status'] == 'pending'
                assert broker_entry['history'] == [{'status': 'pending', 'at': now}]

    def test_reconcile_mark_with_multiple_brokers(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tracker_path = os.path.join(tmpdir, 'tracker.json')
            brokers = {
                'spokeo': {'name': 'Spokeo', 'opt_out_url': 'https://spokeo.com/optout', 'exposure_ids': ['exp-001']},
                'whitepages': {'name': 'WhitePages', 'opt_out_url': 'https://whitepages.com/optout', 'exposure_ids': ['exp-001']},
                'beenverified': {'name': 'BeenVerified', 'opt_out_url': 'https://beenverified.com/optout', 'exposure_ids': ['exp-002']},
            }
            exposures = [
                {
                    'id': 'exp-001',
                    'name': 'Jordan Rivera',
                    'location': 'Portland, OR',
                    'aliases': [],
                    'records': [
                        {'broker': 'Spokeo', 'url': 'https://spokeo.com/Jordan-Rivera', 'location': 'Portland, OR'},
                        {'broker': 'WhitePages', 'url': 'https://whitepages.com/name/Jordan-Rivera', 'location': 'Portland, OR'},
                    ]
                },
                {
                    'id': 'exp-002',
                    'name': 'Jordan Rivera',
                    'location': 'Seattle, WA',
                    'aliases': [],
                    'records': [
                        {'broker': 'BeenVerified', 'url': 'https://www.beenverified.com/Jordan-Rivera', 'location': 'Seattle, WA'},
                    ]
                }
            ]
            marks = [
                {'broker': 'spokeo', 'status': 'submitted'},
                {'broker': 'beenverified', 'status': 'confirmed'},
            ]
            now = '2026-06-12T17:30:00Z'

            counts = reconcile(tracker_path, exposures, brokers, marks, now)

            assert counts == {'pending': 1, 'submitted': 1, 'confirmed': 1}

            with open(tracker_path, 'r') as f:
                data = json.load(f)

            assert data['exposures']['exp-001']['brokers']['spokeo']['status'] == 'submitted'
            assert data['exposures']['exp-001']['brokers']['whitepages']['status'] == 'pending'
            assert data['exposures']['exp-002']['brokers']['beenverified']['status'] == 'confirmed'
