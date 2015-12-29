import logging

import requests

_logger = logging.getLogger(__name__)

__all__ = ['GoDaddyAPI']


class GoDaddyAPI(object):
    _API_TEMPLATE = 'https://api.godaddy.com/v1'

    _GET_DOMAINS = '/domains'
    _GET_DOMAIN = '/domains/{domain}'
    _GET_RECORDS_TYPE_NAME = '/domains/{domain}/records/{type}/@'
    _PUT_RECORDS_TYPE_NAME = '/domains/{domain}/records/{type}/{name}'
    _PATCH_RECORDS = '/domains/{domain}/records'
    _PUT_RECORDS = '/domains/{domain}/records'
    _SSO_KEY_TEMPLATE = 'sso-key {api_key}:{api_secret}'

    def discover_domains(self, account):
        url = self._API_TEMPLATE + self._GET_DOMAINS
        resp = requests.get(url, headers=self._get_auth_headers(account))
        data = resp.json()

        self._log_response_from_method('get', self.discover_domains.__name__, resp)

        domains = list()
        for item in data:
            domain = item['domain']
            if item['status'] == 'ACTIVE':
                domains.append(domain)
                self._display_and_log('Discovered domains: {}'.format(domain))

        return domains

    @staticmethod
    def _display_and_log(message):
        print(message)
        _logger.info(message)

    def get_api_url(self):
        return self._API_TEMPLATE

    def _get_auth_headers(self, account):
        return {
            'Authorization': self._SSO_KEY_TEMPLATE.format(api_key=account['api_key'],
                                                           api_secret=account['api_secret'])}

    def get_domain_info(self, account, domain):
        url = self._API_TEMPLATE + self._GET_DOMAIN.format(domain=domain)
        resp = requests.get(url, headers=self._get_auth_headers(account))
        data = resp.json()
        self._log_response_from_method('get', self.get_domain_info.__name__, resp)

        return data

    def get_domain_a_records(self, account, domain):
        url = self._API_TEMPLATE + self._GET_RECORDS_TYPE_NAME.format(domain=domain, type='A')
        resp = requests.get(url, headers=self._get_auth_headers(account))
        data = resp.json()

        self._log_response_from_method('get', self.get_domain_a_records.__name__, resp)
        self._display_and_log('Retrieved {} records from {}.'.format(len(data), domain))

        return data

    @staticmethod
    def _log_response_from_method(req_type, func_name, resp):
        _logger.info('[{req_type}] {func_name} response: {resp}'.format(func_name=func_name, resp=resp,
                                                                        req_type=req_type.upper()))

    def put_new_a_records(self, account, domain, records):
        url = self._API_TEMPLATE + self._PUT_RECORDS_TYPE_NAME.format(domain=domain, type='A', name='@')

        headers = self._get_auth_headers(account)

        resp = requests.put(url, json=records, headers=headers)
        self._log_response_from_method('put', self.put_new_a_records.__name__, resp)

        if resp.status_code == 200:
            self._display_and_log('Updated {} records @ {}'.format(len(records), domain))

    @staticmethod
    def _remove_key_from_dict(dictionary, key_to_remove):
        return {key: value for key, value in dictionary.items() if key != key_to_remove}

    def update_records_for_account(self, account, ip):
        for domain in self.discover_domains(account):
            records = self.get_domain_a_records(account, domain)

            for record in records:
                data = {'data': ip}
                record.update(data)

            self.put_new_a_records(account, domain, records)
