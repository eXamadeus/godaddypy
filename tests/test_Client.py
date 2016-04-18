import godaddypy

_API_SECRET = 'LWNJoLvEVv6ffgDMTnPnWp'
_API_KEY = 'Uzs41jzo_HftC2uYCXP6VmhZDFi95Br'


class TestClient:
    def __init__(self):
        self.API_TEMPLATE = 'https://api.ote-godaddy.com/v1'

        self.account = godaddypy.Account(_API_KEY, _API_SECRET)

        # Create a Client and override the API to use the test API
        self.client = godaddypy.Client(self.account)
        self.client.API_TEMPLATE = self.API_TEMPLATE

    def test_client_init(self):
        ret = self.client.get_domains()
        assert ret == []

    def test_get_domain_a_record_with_bad_response(self):
        try:
            self.client.get_a_records('somebody.com')
        except godaddypy.client.BadResponse as resp:
            assert resp is not None

    def test_get_domain_schema_for_com(self):
        data = self.client.get_domain_schema()
        assert data is not None
