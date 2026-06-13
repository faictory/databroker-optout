from broker_removal_kit.requests import render_request


SPOKEO_ENTRY = {
    'name': 'Spokeo',
    'recipient': 'privacy@spokeo.com',
    'method': 'email',
    'opt_out_url': 'https://www.spokeo.com/optout',
}

SPOKEO_ENTRY_WITH_VERIFIED = {
    'name': 'Spokeo',
    'recipient': 'privacy@spokeo.com',
    'method': 'email',
    'opt_out_url': 'https://www.spokeo.com/optout',
    'verified_date': '2025-03-01',
}

LISTING_WITH_ALIASES = {
    'name': 'Jordan Rivera',
    'aliases': ['James Rivera'],
    'location': 'Portland, OR',
    'urls': ['https://www.spokeo.com/Jordan-Rivera'],
}

LISTING_NO_ALIASES = {
    'name': 'Jordan Rivera',
    'aliases': [],
    'location': 'Portland, OR',
    'urls': ['https://www.spokeo.com/Jordan-Rivera'],
}

IDENTITY = {
    'name': 'Jordan Rivera',
    'email': 'jordan@example.com',
    'address': 'PO Box 1234, Portland, OR 97201',
}

RUN_DATE = '2026-06-12'


class TestRenderRequestWithIdentity:
    def test_signature_contains_name(self):
        output = render_request(SPOKEO_ENTRY, [LISTING_NO_ALIASES], IDENTITY, RUN_DATE)
        assert 'Jordan Rivera' in output

    def test_signature_contains_email(self):
        output = render_request(SPOKEO_ENTRY, [LISTING_NO_ALIASES], IDENTITY, RUN_DATE)
        assert 'jordan@example.com' in output

    def test_signature_contains_address(self):
        output = render_request(SPOKEO_ENTRY, [LISTING_NO_ALIASES], IDENTITY, RUN_DATE)
        assert 'PO Box 1234, Portland, OR 97201' in output

    def test_signature_format_name_and_email(self):
        output = render_request(SPOKEO_ENTRY, [LISTING_NO_ALIASES], IDENTITY, RUN_DATE)
        assert 'Jordan Rivera <jordan@example.com>' in output

    def test_no_placeholders_with_identity(self):
        output = render_request(SPOKEO_ENTRY, [LISTING_NO_ALIASES], IDENTITY, RUN_DATE)
        assert '<YOUR NAME>' not in output
        assert '<YOUR EMAIL>' not in output
        assert '<YOUR ADDRESS>' not in output


class TestRenderRequestWithoutIdentity:
    def test_placeholder_name(self):
        output = render_request(SPOKEO_ENTRY, [LISTING_NO_ALIASES], None, RUN_DATE)
        assert '<YOUR NAME>' in output

    def test_placeholder_email(self):
        output = render_request(SPOKEO_ENTRY, [LISTING_NO_ALIASES], None, RUN_DATE)
        assert '<YOUR EMAIL>' in output

    def test_placeholder_address(self):
        output = render_request(SPOKEO_ENTRY, [LISTING_NO_ALIASES], None, RUN_DATE)
        assert '<YOUR ADDRESS>' in output

    def test_no_double_angle_brackets_around_email(self):
        output = render_request(SPOKEO_ENTRY, [LISTING_NO_ALIASES], None, RUN_DATE)
        assert '<<YOUR EMAIL>>' not in output

    def test_all_three_placeholders_on_separate_lines(self):
        output = render_request(SPOKEO_ENTRY, [LISTING_NO_ALIASES], None, RUN_DATE)
        assert '<YOUR NAME> <YOUR EMAIL>' in output
        assert '<YOUR ADDRESS>' in output


class TestHeaderFields:
    def test_recipient_in_to_line(self):
        output = render_request(SPOKEO_ENTRY, [LISTING_NO_ALIASES], None, RUN_DATE)
        assert 'To: privacy@spokeo.com' in output

    def test_subject_contains_broker_name(self):
        output = render_request(SPOKEO_ENTRY, [LISTING_NO_ALIASES], None, RUN_DATE)
        assert 'Subject: Opt-out / record removal request — Spokeo' in output

    def test_date_line(self):
        output = render_request(SPOKEO_ENTRY, [LISTING_NO_ALIASES], None, RUN_DATE)
        assert 'Date: 2026-06-12' in output

    def test_method_in_header(self):
        output = render_request(SPOKEO_ENTRY, [LISTING_NO_ALIASES], None, RUN_DATE)
        assert 'Method: email' in output

    def test_opt_out_url_in_header(self):
        output = render_request(SPOKEO_ENTRY, [LISTING_NO_ALIASES], None, RUN_DATE)
        assert 'Opt-out URL: https://www.spokeo.com/optout' in output

    def test_verified_date_from_db_entry(self):
        output = render_request(SPOKEO_ENTRY_WITH_VERIFIED, [LISTING_NO_ALIASES], None, RUN_DATE)
        assert '(Broker procedure last verified: 2025-03-01)' in output

    def test_verified_date_fallback_to_global(self):
        output = render_request(SPOKEO_ENTRY, [LISTING_NO_ALIASES], None, RUN_DATE)
        assert '(Broker procedure last verified: 2026-01-15)' in output

    def test_header_fields_from_entry_not_hardcoded(self):
        custom_entry = {
            'name': 'TestBroker',
            'recipient': 'test@testbroker.example',
            'method': 'web-form',
            'opt_out_url': 'https://testbroker.example/optout',
        }
        output = render_request(custom_entry, [LISTING_NO_ALIASES], None, RUN_DATE)
        assert 'To: test@testbroker.example' in output
        assert 'Opt-out URL: https://testbroker.example/optout' in output
        assert 'Method: web-form' in output
        assert 'Subject: Opt-out / record removal request — TestBroker' in output


class TestListingBullets:
    def test_aliases_clause_present_when_aliases_exist(self):
        output = render_request(SPOKEO_ENTRY, [LISTING_WITH_ALIASES], None, RUN_DATE)
        assert '(also listed as: James Rivera)' in output

    def test_aliases_clause_omitted_when_no_aliases(self):
        output = render_request(SPOKEO_ENTRY, [LISTING_NO_ALIASES], None, RUN_DATE)
        assert 'also listed as' not in output

    def test_name_shown_in_bullet(self):
        output = render_request(SPOKEO_ENTRY, [LISTING_WITH_ALIASES], None, RUN_DATE)
        assert 'Name shown: Jordan Rivera' in output

    def test_location_in_bullet(self):
        output = render_request(SPOKEO_ENTRY, [LISTING_NO_ALIASES], None, RUN_DATE)
        assert 'Location: Portland, OR' in output

    def test_listing_url_in_bullet(self):
        output = render_request(SPOKEO_ENTRY, [LISTING_NO_ALIASES], None, RUN_DATE)
        assert 'Listing: https://www.spokeo.com/Jordan-Rivera' in output

    def test_multiple_listings(self):
        listing2 = {
            'name': 'J. Rivera',
            'aliases': [],
            'location': 'Seattle, WA',
            'urls': ['https://www.spokeo.com/J-Rivera-Seattle'],
        }
        output = render_request(SPOKEO_ENTRY, [LISTING_NO_ALIASES, listing2], None, RUN_DATE)
        assert 'Portland, OR' in output
        assert 'Seattle, WA' in output
