from godaddypy import Account, Client

_API_SECRET = 'LWNJoLvEVv6ffgDMTnPnWp'
_API_KEY = 'Uzs41jzo_HftC2uYCXP6VmhZDFi95Br'


class TestClient:
    def __init__(self):
        self.API_TEMPLATE = 'https://api.ote-godaddy.com/v1'

        self.GET_DOMAINS = '/domains'
        self.GET_DOMAIN = '/domains/{domain}'
        self.GET_RECORDS_TYPE_NAME = '/domains/{domain}/records/{type}/@'
        self.PUT_RECORDS_TYPE_NAME = '/domains/{domain}/records/{type}/{name}'
        self.PATCH_RECORDS = '/domains/{domain}/records'
        self.PUT_RECORDS = '/domains/{domain}/records'

        self.account = Account(_API_KEY, _API_SECRET)

        # Create a Client and override the API to use the test API
        self.client = Client(self.account)
        self.client.API_TEMPLATE = self.API_TEMPLATE

    def test_client_init(self):
        self.client.get_domains()

    def test_update_ip(self):
        self.client.update_ip('1.2.3.4')
