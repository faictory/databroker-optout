import os
import json
import tempfile
from broker_removal_kit.cli import main


class TestConfigPriorityAndSignatureFill:
    def test_config_deadname_priority_and_identity_fill(self, capsys):
        """Integration test: --config priority and signature fill.

        Invokes CLI on examples/sample.csv --config examples/brk.toml with --out to tmp dir.
        Asserts:
        - exp-001 Portland Jordan Rivera exposure is high priority
        - deadname_matches entry for James Rivera
        - request files contain requester identity, not placeholders
        """
        with tempfile.TemporaryDirectory() as out_dir:
            result = main([
                'examples/sample.csv',
                '--config', 'examples/brk.toml',
                '--out', out_dir,
                '--format', 'json'
            ])
            assert result == 0

            # Verify CLI output contains high priority exp-001 with deadname match
            captured = capsys.readouterr()
            output = json.loads(captured.out)

            # Find exp-001 Portland exposure
            exp_001 = None
            for exposure in output.get('exposures', []):
                if (exposure.get('id') == 'exp-001' and
                    exposure.get('location') == 'Portland, OR'):
                    exp_001 = exposure
                    break

            assert exp_001 is not None, "exp-001 Portland not found in exposures"
            assert exp_001.get('priority') == 'high', "exp-001 should be high priority"
            assert 'James Rivera' in exp_001.get('deadname_matches', []), \
                "exp-001 should have deadname_matches for James Rivera"

            # Verify request file contains requester identity, not placeholders
            requests_dir = os.path.join(out_dir, 'requests')
            spokeo_request = os.path.join(requests_dir, 'spokeo.txt')

            assert os.path.exists(spokeo_request), "spokeo.txt request file not written"

            with open(spokeo_request) as f:
                content = f.read()

            # Verify identity is filled
            assert 'Jordan Rivera' in content, "requester name not in request"
            assert 'jordan@example.com' in content, "requester email not in request"
            assert 'PO Box 1234, Portland, OR 97201' in content, "requester address not in request"

            # Verify no placeholders
            assert '<YOUR NAME>' not in content, "placeholder name should not be in request"
            assert '<YOUR EMAIL>' not in content, "placeholder email should not be in request"
            assert '<YOUR ADDRESS>' not in content, "placeholder address should not be in request"
