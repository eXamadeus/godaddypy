import godaddypy

_API_SECRET = 'LWNJoLvEVv6ffgDMTnPnWp'
_API_KEY = 'Uzs41jzo_HftC2uYCXP6VmhZDFi95Br'


class TestClient(godaddypy.Client):
    def __init__(self):
        self.account = godaddypy.Account(_API_KEY, _API_SECRET)
        # Create a Client and override the API to use the test API
        super(TestClient, self).__init__(self.account)
        self.API_TEMPLATE = 'https://api.ote-godaddy.com/v1'

    def test_client_init(self):
        ret = self.get_domains()
        print(ret)
        if 'code' in ret:
            if ret['code'] is not 'ERROR_INTERNAL':  # as long as we don't see a server error
                assert ret == []

    def test_get_domain_a_record_with_bad_response(self):
        try:
            self.get_a_records('somebody.com')
        except godaddypy.client.BadResponse as resp:
            assert resp is not None

    def test_get_domain_schema_for_com(self):
        data = self.get_domain_schema()
        assert data is not None
