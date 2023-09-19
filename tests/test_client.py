from __future__ import unicode_literals

import logging

# noinspection PyPackageRequirements
from callee import EndsWith

# noinspection PyPackageRequirements
from mock import patch

from godaddypy import Account, Client
from godaddypy.client import BadResponse


class TestClient(object):
    account: Account
    client: Client
    logger: logging.Logger

    @classmethod
    def setup_class(cls):
        cls.logger = logging.getLogger(cls.__name__)
        cls.logger.setLevel(logging.INFO)

        cls.account = Account("", "")
        # Create a Client and override the API to use the test API
        cls.client = Client(cls.account, log_level=logging.WARNING)
        cls.client.API_TEMPLATE = "https://api.ote-godaddy.com/v1"

        cls.fake_records = [
            {"name": "test1", "ttl": 3600, "data": "127.0.0.1", "type": "A"},
            {"name": "test2", "ttl": 3600, "data": "192.168.0.1", "type": "A"},
        ]

    @patch.object(Client, "_get_json_from_response")
    def test_get_domains(self, mock):
        mock.return_value = [
            {"domainId": 123, "domain": "123.com", "status": "ACTIVE"},
            {"domainId": 456, "domain": "abc.edu", "status": "ACTIVE"},
            {"domainId": 456, "domain": "old.net", "status": "INACTIVE"},
        ]
        domains = self.client.get_domains()
        assert "123.com" in domains and "abc.edu" in domains

    @patch.object(Client, "_get_json_from_response")
    def test_get_domain_a_record_with_bad_response(self, mock):
        mock.side_effect = BadResponse("You 'dun goofed boy!")
        did_raise = False

        try:
            self.client.get_records("somebody.com", record_type="A")
        except BadResponse as resp:
            did_raise = True
            assert resp is not None

        assert did_raise

    @patch.object(Client, "_put")
    def test_update_record(self, put_mock):
        self.client.update_record("test.com", self.fake_records[0])
        put_mock.assert_called_once_with(
            EndsWith("/v1/domains/test.com/records/A/test1"),
            json=[self.fake_records[0]],
        )

    @patch.object(Client, "update_record")
    @patch.object(Client, "get_records")
    def test_update_ip(self, get_mock, update_mock):
        new_ip = "1.2.3.4"

        get_mock.return_value = [self.fake_records[0]]

        self.client.update_ip(new_ip, domains=["abc.com"])

        expected = self.fake_records[0].copy()
        expected.update(data=new_ip)
        update_mock.assert_called_once_with("abc.com", expected)

    @patch.object(Client, "_delete")
    @patch.object(Client, "get_records")
    def test_delete_records(self, get_mock, delete_mock):
        fake_domain = "apple.com"
        fake_records = [
            {"name": "test1", "data": "127.0.0.1", "type": "A"},
            {"name": "test2", "data": "192.168.0.1", "type": "A"},
        ]

        get_mock.return_value = fake_records

        self.client.delete_records(fake_domain, "test2")

        delete_mock.assert_called_once_with(url=EndsWith("/v1/domains/apple.com/records/A/test2"))

    def test_account_without_delegate(self):
        _PRIVATE_KEY = "blahdeyblah"
        _PUBLIC_KEY = "hooeybalooooooeryasdfasdfsdfs"

        acct = Account(api_key=_PUBLIC_KEY, api_secret=_PRIVATE_KEY)

        assert "Authorization" in acct.get_headers()
        assert acct.get_headers()["Authorization"] == Account._SSO_KEY_TEMPLATE.format(
            api_secret=_PRIVATE_KEY, api_key=_PUBLIC_KEY
        )

    def test_account_with_delegate(self):
        _DELEGATE_ID = "1234987234jdsfasdf"
        _PRIVATE_KEY = "blahdeyblah"
        _PUBLIC_KEY = "hooeybalooooooeryasdfasdfsdfs"

        acct = Account(api_key=_PUBLIC_KEY, api_secret=_PRIVATE_KEY, delegate=_DELEGATE_ID)

        assert "X-Shopper-Id" in acct.get_headers()
        assert "Authorization" in acct.get_headers()
        assert acct.get_headers()["X-Shopper-Id"] == _DELEGATE_ID
        assert acct.get_headers()["Authorization"] == Account._SSO_KEY_TEMPLATE.format(
            api_secret=_PRIVATE_KEY, api_key=_PUBLIC_KEY
        )

    def test_build_record_url_happy_path(self):
        domains = ["test.com", "apple.com", "google.com", "aol.com"]
        names = ["@", None, "someName", None]
        types = ["A", "AAAA", "DNS", None]

        expected = [
            self.client.API_TEMPLATE
            + self.client.RECORDS_TYPE_NAME.format(domain=domains[0], name=names[0], type=types[0]),
            self.client.API_TEMPLATE + self.client.RECORDS_TYPE.format(domain=domains[1], type=types[1]),
            self.client.API_TEMPLATE
            + self.client.RECORDS_TYPE_NAME.format(domain=domains[2], name=names[2], type=types[2]),
            self.client.API_TEMPLATE + self.client.RECORDS.format(domain=domains[3]),
        ]

        urls = list()

        if len(domains) == len(names) == len(types) == len(expected):
            for i, val in enumerate(domains):
                urls.append(self.client._build_record_url(val, name=names[i], record_type=types[i]))
                assert urls[i] == expected[i]
        else:
            raise ValueError(
                "The test {} has invalid internal parameters!".format(self.test_build_record_url_happy_path.__name__)
            )

    def test_build_record_url_raise_value_error(self):
        raised = False

        try:
            self.client._build_record_url("test.com", None, "blah")
        except ValueError:
            raised = True

        assert raised
