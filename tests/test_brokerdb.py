from broker_removal_kit.brokerdb import slugify, lookup, verified_date, broker_count


class TestSlugify:
    def test_spokeo(self):
        assert slugify('Spokeo') == 'spokeo'

    def test_whitepages(self):
        assert slugify('WhitePages') == 'whitepages'

    def test_truepeoplesearch(self):
        assert slugify('TruePeopleSearch') == 'truepeoplesearch'

    def test_strips_non_alphanumeric(self):
        assert slugify('Some-Broker!') == 'somebroker'


class TestLookup:
    def test_known_broker_by_name_returns_real_data(self):
        result = lookup('Spokeo')
        assert result['name'] == 'Spokeo'
        assert result['recipient'] == 'privacy@spokeo.com'
        assert result['method'] == 'email'
        assert result['opt_out_url'] == 'https://www.spokeo.com/optout'

    def test_known_broker_by_slug(self):
        result = lookup('spokeo')
        assert result['name'] == 'Spokeo'
        assert result['recipient'] == 'privacy@spokeo.com'

    def test_known_broker_case_insensitive(self):
        result = lookup('SPOKEO')
        assert result['name'] == 'Spokeo'

    def test_known_broker_whitepages(self):
        result = lookup('WhitePages')
        assert result['name'] == 'WhitePages'
        assert result['recipient'] == 'support@whitepages.com'
        assert result['opt_out_url'] == 'https://www.whitepages.com/suppression'

    def test_known_broker_truepeoplesearch(self):
        result = lookup('TruePeopleSearch')
        assert result['name'] == 'TruePeopleSearch'
        assert result['recipient'] == 'privacy@truepeoplesearch.com'

    def test_unknown_broker_does_not_raise(self):
        result = lookup('SomeUnknownBrokerXYZ')
        assert result is not None

    def test_unknown_broker_returns_fallback_name(self):
        result = lookup('SomeUnknownBrokerXYZ')
        assert result['name'] == 'SomeUnknownBrokerXYZ'

    def test_unknown_broker_method_is_email(self):
        result = lookup('SomeUnknownBrokerXYZ')
        assert result['method'] == 'email'

    def test_unknown_broker_has_all_required_keys(self):
        result = lookup('SomeUnknownBrokerXYZ')
        assert 'name' in result
        assert 'recipient' in result
        assert 'method' in result
        assert 'opt_out_url' in result


class TestVerifiedDate:
    def test_verified_date_matches_spec(self):
        assert verified_date() == '2026-01-15'


class TestBrokerCount:
    def test_broker_count_is_twelve(self):
        assert broker_count() == 12

    def test_broker_count_is_positive_int(self):
        count = broker_count()
        assert isinstance(count, int)
        assert count > 0
