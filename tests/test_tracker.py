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
            assert len(data['brokers']) == 2
            assert 'spokeo' in data['brokers']
            assert 'whitepages' in data['brokers']
            assert data['brokers']['spokeo']['status'] == 'pending'
            assert data['brokers']['whitepages']['status'] == 'pending'
            assert data['brokers']['spokeo']['history'] == [{'status': 'pending', 'at': now}]
            assert data['brokers']['spokeo']['exposure_ids'] == ['exp-001']

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

            assert data['brokers']['spokeo']['status'] == 'pending'
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

            history = data['brokers']['spokeo']['history']
            assert len(history) == 2
            assert history[0] == {'status': 'pending', 'at': first_now}
            assert history[1] == {'status': 'submitted', 'at': second_now}
            assert data['brokers']['spokeo']['status'] == 'submitted'

    def test_reconcile_mark_no_change_doesnt_append_history(self):
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

            second_marks = [{'broker': 'spokeo', 'status': 'pending'}]
            second_now = '2026-06-13T10:00:00Z'
            reconcile(tracker_path, exposures, brokers, second_marks, second_now)

            with open(tracker_path, 'r') as f:
                data = json.load(f)

            assert data['brokers']['spokeo']['status'] == 'pending'
            assert len(data['brokers']['spokeo']['history']) == 1

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
                'whitepages': {'name': 'WhitePages', 'opt_out_url': 'https://whitepages.com/optout', 'exposure_ids': ['exp-002']},
            }
            exposures_2 = [
                exposures_1[0],
                {
                    'id': 'exp-002',
                    'name': 'Alex Smith',
                    'location': 'Seattle, WA',
                    'aliases': [],
                    'records': [
                        {'broker': 'WhitePages', 'url': 'https://whitepages.com/name/Alex-Smith', 'location': 'Seattle, WA'},
                    ]
                }
            ]

            second_now = '2026-06-13T10:00:00Z'
            counts = reconcile(tracker_path, exposures_2, second_brokers, [], second_now)

            assert counts == {'pending': 2, 'submitted': 0, 'confirmed': 0}

            with open(tracker_path, 'r') as f:
                data = json.load(f)

            assert len(data['brokers']) == 2
            assert 'spokeo' in data['brokers']
            assert 'whitepages' in data['brokers']
            assert data['brokers']['spokeo']['status'] == 'pending'
            assert data['brokers']['whitepages']['status'] == 'pending'
            assert data['brokers']['spokeo']['exposure_ids'] == ['exp-001']
            assert data['brokers']['whitepages']['exposure_ids'] == ['exp-002']

    def test_reconcile_broker_appears_in_multiple_exposures(self):
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
                        {'broker': 'Spokeo', 'url': 'https://spokeo.com/Jordan-Rivera-Seattle', 'location': 'Seattle, WA'},
                    ]
                }
            ]
            now = '2026-06-12T17:30:00Z'

            counts = reconcile(tracker_path, exposures, brokers, [], now)

            assert counts == {'pending': 1, 'submitted': 0, 'confirmed': 0}

            with open(tracker_path, 'r') as f:
                data = json.load(f)

            assert len(data['brokers']) == 1
            assert data['brokers']['spokeo']['status'] == 'pending'
            assert sorted(data['brokers']['spokeo']['exposure_ids']) == ['exp-001', 'exp-002']

    def test_reconcile_handles_missing_tracker_file(self):
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
            now = '2026-06-12T17:30:00Z'

            counts = reconcile(tracker_path, exposures, brokers, [], now)

            assert counts == {'pending': 1, 'submitted': 0, 'confirmed': 0}
            assert os.path.exists(tracker_path)

    def test_reconcile_creates_parent_directories(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tracker_path = os.path.join(tmpdir, 'nested', 'dir', 'tracker.json')
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
            now = '2026-06-12T17:30:00Z'

            counts = reconcile(tracker_path, exposures, brokers, [], now)

            assert counts == {'pending': 1, 'submitted': 0, 'confirmed': 0}
            assert os.path.exists(tracker_path)

    def test_reconcile_handles_corrupted_tracker_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tracker_path = os.path.join(tmpdir, 'tracker.json')

            with open(tracker_path, 'w') as f:
                f.write('{ invalid json }')

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
            now = '2026-06-12T17:30:00Z'

            counts = reconcile(tracker_path, exposures, brokers, [], now)

            assert counts == {'pending': 1, 'submitted': 0, 'confirmed': 0}

            with open(tracker_path, 'r') as f:
                data = json.load(f)

            assert data['version'] == 1
            assert data['brokers']['spokeo']['status'] == 'pending'

    def test_reconcile_all_statuses(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tracker_path = os.path.join(tmpdir, 'tracker.json')
            brokers = {
                'spokeo': {'name': 'Spokeo', 'opt_out_url': 'https://spokeo.com/optout', 'exposure_ids': ['exp-001']},
                'whitepages': {'name': 'WhitePages', 'opt_out_url': 'https://whitepages.com/optout', 'exposure_ids': ['exp-001']},
                'beenverified': {'name': 'BeenVerified', 'opt_out_url': 'https://beenverified.com/optout', 'exposure_ids': ['exp-001']},
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
                        {'broker': 'BeenVerified', 'url': 'https://beenverified.com/Jordan-Rivera', 'location': 'Portland, OR'},
                    ]
                }
            ]
            now = '2026-06-12T17:30:00Z'

            marks = [
                {'broker': 'spokeo', 'status': 'submitted'},
                {'broker': 'beenverified', 'status': 'confirmed'},
            ]

            counts = reconcile(tracker_path, exposures, brokers, marks, now)

            assert counts == {'pending': 1, 'submitted': 1, 'confirmed': 1}

            with open(tracker_path, 'r') as f:
                data = json.load(f)

            assert data['brokers']['spokeo']['status'] == 'submitted'
            assert data['brokers']['whitepages']['status'] == 'pending'
            assert data['brokers']['beenverified']['status'] == 'confirmed'

    def test_reconcile_empty_exposures_list(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tracker_path = os.path.join(tmpdir, 'tracker.json')
            brokers = {}
            exposures = []
            now = '2026-06-12T17:30:00Z'

            counts = reconcile(tracker_path, exposures, brokers, [], now)

            assert counts == {'pending': 0, 'submitted': 0, 'confirmed': 0}

            with open(tracker_path, 'r') as f:
                data = json.load(f)

            assert len(data['brokers']) == 0

    def test_reconcile_marks_multiple_status_changes(self):
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
            now_1 = '2026-06-12T17:30:00Z'
            now_2 = '2026-06-13T10:00:00Z'
            now_3 = '2026-06-14T15:00:00Z'

            reconcile(tracker_path, exposures, brokers, [], now_1)

            reconcile(tracker_path, exposures, brokers, [{'broker': 'spokeo', 'status': 'submitted'}], now_2)

            reconcile(tracker_path, exposures, brokers, [{'broker': 'spokeo', 'status': 'confirmed'}], now_3)

            with open(tracker_path, 'r') as f:
                data = json.load(f)

            history = data['brokers']['spokeo']['history']
            assert len(history) == 3
            assert history[0]['status'] == 'pending'
            assert history[1]['status'] == 'submitted'
            assert history[2]['status'] == 'confirmed'
