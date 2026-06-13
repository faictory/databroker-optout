import os
import json
from broker_removal_kit.cli import main


class TestMarkPersistenceAcrossRuns:
    def test_mark_submission_persists_across_runs(self, tmp_path):
        """Test that --mark spokeo=submitted persists across a second run without --mark."""
        out_dir = str(tmp_path)

        # First run: mark Spokeo as submitted
        result1 = main(['examples/sample.csv', '--out', out_dir, '--mark', 'spokeo=submitted'])
        assert result1 == 0

        # Verify first run tracker state
        tracker_path = os.path.join(out_dir, 'tracker.json')
        with open(tracker_path) as f:
            tracker1 = json.load(f)

        assert tracker1['brokers']['spokeo']['status'] == 'submitted'
        counts1 = {
            'pending': sum(1 for b in tracker1['brokers'].values() if b['status'] == 'pending'),
            'submitted': sum(1 for b in tracker1['brokers'].values() if b['status'] == 'submitted'),
            'confirmed': sum(1 for b in tracker1['brokers'].values() if b['status'] == 'confirmed')
        }

        # Second run: no --mark flag, same input and output directory
        result2 = main(['examples/sample.csv', '--out', out_dir])
        assert result2 == 0

        # Verify second run tracker state: Spokeo should still be submitted
        with open(tracker_path) as f:
            tracker2 = json.load(f)

        assert tracker2['brokers']['spokeo']['status'] == 'submitted'
        counts2 = {
            'pending': sum(1 for b in tracker2['brokers'].values() if b['status'] == 'pending'),
            'submitted': sum(1 for b in tracker2['brokers'].values() if b['status'] == 'submitted'),
            'confirmed': sum(1 for b in tracker2['brokers'].values() if b['status'] == 'confirmed')
        }

        # Verify counts are unchanged
        assert counts2['pending'] == counts1['pending']
        assert counts2['submitted'] == counts1['submitted']
        assert counts2['confirmed'] == counts1['confirmed']
