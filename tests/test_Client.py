from godaddypy import Account, Client

_API_SECRET = 'VPfo9mESjwPzR3DYqdaF2n'
_API_KEY = 'Uzs41jzo_VPfjZXt5JjMP6v1tuM4TT4'


class TestClient:
    def __init__(self):
        self.API_TEMPLATE = 'https://api.ote-godaddy.com'

        self.GET_DOMAINS = '/domains'
        self.GET_DOMAIN = '/domains/{domain}'
        self.GET_RECORDS_TYPE_NAME = '/domains/{domain}/records/{type}/@'
        self.PUT_RECORDS_TYPE_NAME = '/domains/{domain}/records/{type}/{name}'
        self.PATCH_RECORDS = '/domains/{domain}/records'
        self.PUT_RECORDS = '/domains/{domain}/records'

        self.account = Account(_API_KEY, _API_SECRET)

    def test_client_init(self):
        client = Client(self.account)

        print(client.get_domains())
