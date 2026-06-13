import pytest
from broker_removal_kit.tracker import parse_mark
from broker_removal_kit.errors import BrokerKitError


class TestParseMark:
    def test_parse_mark_valid_pending(self):
        result = parse_mark('spokeo=pending')
        assert result == {'broker': 'spokeo', 'status': 'pending'}

    def test_parse_mark_valid_submitted(self):
        result = parse_mark('spokeo=submitted')
        assert result == {'broker': 'spokeo', 'status': 'submitted'}

    def test_parse_mark_valid_confirmed(self):
        result = parse_mark('spokeo=confirmed')
        assert result == {'broker': 'spokeo', 'status': 'confirmed'}

    def test_parse_mark_with_whitespace(self):
        result = parse_mark('  spokeo  =  pending  ')
        assert result == {'broker': 'spokeo', 'status': 'pending'}

    def test_parse_mark_missing_equals_raises_error(self):
        with pytest.raises(BrokerKitError, match="invalid mark format"):
            parse_mark('spokeo-pending')

    def test_parse_mark_no_status_raises_error(self):
        with pytest.raises(BrokerKitError, match="invalid mark format"):
            parse_mark('spokeo')

    def test_parse_mark_invalid_status_raises_error(self):
        with pytest.raises(BrokerKitError, match="invalid status"):
            parse_mark('spokeo=invalid')

    def test_parse_mark_invalid_status_done_raises_error(self):
        with pytest.raises(BrokerKitError, match="invalid status"):
            parse_mark('spokeo=done')

    def test_parse_mark_empty_status_raises_error(self):
        with pytest.raises(BrokerKitError, match="invalid status"):
            parse_mark('spokeo=')
