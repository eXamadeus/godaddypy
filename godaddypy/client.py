import logging

import requests

__all__ = ['Client']

logging.basicConfig(filename='GoDaddyClient.log',
                    filemode='a',
                    level=logging.INFO)


def _get(url, method_name, **kwargs):
    resp = requests.get(url, **kwargs)
    _log_response_from_method('get', method_name, resp)
    _validate_response_success(resp)
    return resp


def _put(url, method_name, **kwargs):
    resp = requests.put(url, **kwargs)
    _log_response_from_method('put', method_name, resp)
    _validate_response_success(resp)
    return resp


def _log(message):
    logging.info(message)


def _log_response_from_method(req_type, resp):
    logging.info('[{req_type}] response: {resp}'.format(resp=resp, req_type=req_type.upper()))
    logging.debug('Response data: {}'.format(resp.content))


def _remove_key_from_dict(dictionary, key_to_remove):
    return {key: value for key, value in dictionary.items() if key != key_to_remove}


def _validate_response_success(response):
    if response.status_code != 200:
        raise BadResponse(response.json())


class Client(object):
    _API_TEMPLATE = 'https://api.godaddy.com/v1'

    _GET_DOMAINS = '/domains'
    _GET_DOMAIN = '/domains/{domain}'
    _GET_RECORDS_TYPE_NAME = '/domains/{domain}/records/{type}/@'
    _PUT_RECORDS_TYPE_NAME = '/domains/{domain}/records/{type}/{name}'
    _PATCH_RECORDS = '/domains/{domain}/records'
    _PUT_RECORDS = '/domains/{domain}/records'

    _account = None

    def __init__(self, account):
        self._account = account

    def _get_headers(self):
        return self._account.get_auth_headers()

    def _scope_control_account(self, account):
        if account is None:
            return self._account
        else:
            return account

    def get_domains(self):
        url = self._API_TEMPLATE + self._GET_DOMAINS
        data = _get(url, method_name=self.get_domains.__name__, headers=self._get_headers()).json()

        domains = list()
        for item in data:
            domain = item['domain']
            if item['status'] == 'ACTIVE':
                domains.append(domain)
                _log('Discovered domains: {}'.format(domain))

        return domains

    def get_api_url(self):
        return self._API_TEMPLATE

    def get_domain_info(self, domain):
        url = self._API_TEMPLATE + self._GET_DOMAIN.format(domain=domain)
        return _get(url, method_name=self.get_domain_info.__name__, headers=self._get_headers()).json()

    def get_a_records(self, domain):
        url = self._API_TEMPLATE + self._GET_RECORDS_TYPE_NAME.format(domain=domain, type='A')
        data = _get(url, method_name=self.get_a_records.__name__, headers=self._get_headers()).json()

        _log('Retrieved {} records from {}.'.format(len(data), domain))

        return data

    def put_new_a_records(self, domain, records):
        url = self._API_TEMPLATE + self._PUT_RECORDS_TYPE_NAME.format(domain=domain, type='A', name='@')
        _put(url, json=records, method_name=self.get_a_records.__name__, headers=self._get_headers())
        _log('Updated {} records @ {}'.format(len(records), domain))

    def update_ip(self, ip, domains=None):
        """Update the IP address in all A records to the value of ip.  Returns True if no exceptions occured during
        the update.

        If no domains are provided, all domains will be updated.
        """
        if domains is None:
            domains = self.get_domains()

        for domain in domains:
            records = self.get_a_records(domain)

            for record in records:
                data = {'data': ip}
                record.update(data)

            self.put_new_a_records(domain, records)

        # If we didn't get any exceptions, return True to let the user know
        return True


class BadResponse(Exception):
    def __init__(self, message, *args, **kwargs):
        self._message = message
        super(*args, **kwargs)

    def __str__(self, *args, **kwargs):
        return 'Response Data: {}'.format(self._message)
