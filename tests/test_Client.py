import logging

import callee
from mock import patch

from godaddypy import Client, Account
from godaddypy.client import BadResponse

_API_SECRET = 'LWNJoLvEVv6ffgDMTnPnWp'
_API_KEY = 'Uzs41jzo_HftC2uYCXP6VmhZDFi95Br'


class TestClient:
    @classmethod
    def setup_class(cls):
        cls.logger = logging.getLogger(cls.__name__)
        cls.logger.setLevel(logging.INFO)

        cls.account = Account(_API_KEY, _API_SECRET)
        # Create a Client and override the API to use the test API
        cls.client = Client(cls.account, log_level=logging.WARNING)
        cls.client.API_TEMPLATE = 'https://api.ote-godaddy.com/v1'

    @patch.object(Client, '_get_json_from_response')
    def test_get_domains(self, mock):
        mock.return_value = [{"domainId": 123, "domain": "123.com", "status": "ACTIVE"},
                             {"domainId": 456, "domain": "abc.edu", "status": "ACTIVE"},
                             {"domainId": 456, "domain": "old.net", "status": "INACTIVE"}]
        domains = self.client.get_domains()
        assert u'123.com' in domains and u'abc.edu' in domains

    @patch.object(Client, '_get_json_from_response')
    def test_get_domain_a_record_with_bad_response(self, mock):
        mock.side_effect = BadResponse("You 'dun goofed boy!")
        did_raise = False

        try:
            self.client.get_records('somebody.com', 'A')
        except BadResponse as resp:
            did_raise = True
            assert resp is not None

        assert did_raise

    @patch.object(Client, 'update_record')
    @patch.object(Client, 'get_records')
    def test_update_ip(self, get_mock, update_mock):
        fake_record = {'name': 'test', 'data': '0.0.0.0'}
        new_ip = '1.2.3.4'

        get_mock.return_value = [fake_record]

        self.client.update_ip(new_ip, domains=['abc.com'])

        fake_record.update(data=new_ip)
        update_mock.assert_called_once_with('abc.com', fake_record)

    @patch.object(Client, '_put')
    @patch.object(Client, 'get_records')
    def test_delete_records(self, get_mock, put_mock):
        fake_domain = 'apple.com'
        fake_records = [{'name': 'test1', 'data': '127.0.0.1', 'type': 'A'},
                        {'name': 'test2', 'data': '192.168.0.1', 'type': 'A'}]

        get_mock.return_value = fake_records

        self.client.delete_records(fake_domain, 'test2')

        put_mock.assert_called_once_with(callee.String(), json=[fake_records[0]])
