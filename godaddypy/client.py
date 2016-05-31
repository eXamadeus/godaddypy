import logging

import requests

__all__ = ['Client']


class Client(object):
    """The GoDaddyPy Client.

    This client is used to connect to the GoDaddy API and to perform requests with said API.
    """

    def __init__(self, account, logging_handler=logging.StreamHandler()):
        """Create a new `godaddypy.Client` object

        :type account: godaddypy.Account
        :param account: The godaddypy.Account object to create auth headers with.
        """

        # Logging setup
        self.logger = logging.getLogger(__name__)
        logging_handler.setLevel(logging.INFO)
        self.logger.addHandler(logging_handler)

        # Templates
        self.API_TEMPLATE = 'https://api.godaddy.com/v1'
        self.GET_DOMAINS = '/domains'
        self.GET_DOMAIN = '/domains/{domain}'
        self.GET_RECORDS_TYPE_NAME = '/domains/{domain}/records/{type}/'
        self.PUT_RECORDS_TYPE_NAME = '/domains/{domain}/records/{type}/{name}'
        self.PATCH_RECORDS = '/domains/{domain}/records'
        self.PUT_RECORDS = '/domains/{domain}/records'
        self.GET_DOMAIN_PURCHASE_SCHEMA = '/domains/purchase/schema/{tld}'
        self.GET_RECORD_TYPE_NAME = '/domains/{domain}/records/{type}/{name}'

        self.account = account

    def _log_response_from_method(self, req_type, resp):
        self.logger.info('[{req_type}] response: {resp}'.format(resp=resp, req_type=req_type.upper()))
        self.logger.debug('Response data: {}'.format(resp.content))

    @staticmethod
    def _remove_key_from_dict(dictionary, key_to_remove):
        return {key: value for key, value in dictionary.items() if key != key_to_remove}

    @staticmethod
    def _validate_response_success(response):
        if response.status_code != 200:
            raise BadResponse(response.json())

    def _get(self, url, **kwargs):
        resp = requests.get(url, **kwargs)
        self._log_response_from_method('get', resp)
        self._validate_response_success(resp)
        return resp

    def _get_headers(self):
        return self.account.get_auth_headers()

    def _put(self, url, **kwargs):
        resp = requests.put(url, **kwargs)
        self._log_response_from_method('put', resp)
        self._validate_response_success(resp)
        return resp

    def _scope_control_account(self, account):
        if account is None:
            return self.account
        else:
            return account

    def get_domains(self):
        url = self.API_TEMPLATE + self.GET_DOMAINS
        data = self._get(url, headers=self._get_headers()).json()

        domains = list()
        for item in data:
            domain = item['domain']
            if item['status'] == 'ACTIVE':
                domains.append(domain)
                self.logger.info('Discovered domains: {}'.format(domain))

        return domains

    def get_domain_schema(self, tld='com'):
        """Get the purchase request schema for a specified top level domain (tld)

        :param tld: The top level domain (ex: 'com', 'edu', 'gov')
        :type tld: str

        :return: The purchase request schema as a JSON string
        """
        url = self.API_TEMPLATE + self.GET_DOMAIN_PURCHASE_SCHEMA.format(tld=tld)
        return self._get(url=url, headers=self._get_headers()).json()

    def get_api_url(self):
        return self.API_TEMPLATE

    def get_domain_info(self, domain):
        """Get the GoDaddy supplied information about a specific domain.

        :param domain: The domain to obtain info about.
        :type domain: str

        :return A JSON string representing the domain information
        """
        url = self.API_TEMPLATE + self.GET_DOMAIN.format(domain=domain)
        return self._get(url, headers=self._get_headers()).json()

    def get_a_records(self, domain):
        url = self.API_TEMPLATE + self.GET_RECORDS_TYPE_NAME.format(domain=domain, type='A')
        data = self._get(url, headers=self._get_headers()).json()

        self.logger.info('Retrieved {} records from {}.'.format(len(data), domain))

        return data

    def put_a_records(self, domain, records):
        for _rec in records:
            url = self.API_TEMPLATE + self.PUT_RECORDS_TYPE_NAME.format(domain=domain, type='A', name=_rec['name'])
            self._put(url, json=_rec, headers=self._get_headers())
            logging.info('Updated {} records @ {}'.format(len(records), domain))

    def put_records(self, record_type, domain, records):
        for _rec in records:
            url = self.API_TEMPLATE + self.PUT_RECORDS_TYPE_NAME.format(domain=domain, type=record_type,
                                                                        name=_rec['name'])
            self._put(url, json=_rec, headers=self._get_headers())
            logging.info('Updated {} records @ {}'.format(len(records), domain))

    def update_ip(self, ip, domains=None, subdomains=None):
        """Update the IP address in all A records to the value of ip.  Returns True if no exceptions occurred during
        the update.  If no domains are provided, all domains returned from self.get_domains() will be updated.

        :param ip: The new IP address (eg. '123.1.2.255')
        :param domains: A list of the domains you want to update (eg. ['123.com','abc.net'])
        :param subdomains: A list of the subdomains you want to update (eg. ['www','dev'])

        :type ip: str
        :type domains: str, list of str
        :type subdomains: str, list of str
        """

        if domains is None:
            domains = self.get_domains()
        elif type(domains) == str:
            domains = [domains]
        elif type(domains) == list:
            pass
        else:
            raise SystemError("Domains must be type 'list' or type 'str'")

        for domain in domains:
            records = self.get_a_records(domain)
            new_records = []
            for record in records:
                r_name = str(record['name'])
                r_ip = str(record['data'])

                if not r_ip == ip:

                    if ((subdomains is None) or
                            (type(subdomains) == list and subdomains.count(r_name)) or
                            (type(subdomains) == str and subdomains == r_name)):
                        data = {'data': str(ip)}
                        record.update(data)

                        new_records.append(record)

            self.put_a_records(domain, new_records)

        # If we didn't get any exceptions, return True to let the user know
        return True

    def get_record(self, domain, name, type):
        """Returns information from a single DNS record."""
        url = self.API_TEMPLATE +\
              self.GET_RECORD_TYPE_NAME.format(domain = domain, type = type,
                                               name = name)
        data = self._get(url, headers = self._get_headers()).json()
        self.logger.info('Retrieved {} record from {}.'.format(len(data), domain))
        return data[0]

    def update_record_ip(self, ip, domain, name, type):
        """Update the IP address for a single record

        ip -- the new IP for the DNS record (ex. '123.1.2.255')
        domain -- the domain where the DNS belongs to (ex. 'example.com')
        name -- the DNS record name to be updated (ex. 'dynamic')
        type -- Record type (ex. 'CNAME', 'A'...)
        """

        record = self.get_record(domain, name, type)
        data = {'data': str(ip)}
        record.update(data)
        self._put_record(domain, record)

        # If we didn't get any exceptions, return True to let the user know
        return True

    def _put_record(self, domain, record):
        """Call to godaddy API to update a single DNS record

        domain -- the domain where the DNS belongs to (eg. 'example.com')
        record -- dict with record info (ex. {'name': 'dynamic', 'ttl': 3600,
                  'data': '1.1.1.1', 'type': 'A'})
        """
        url = self.API_TEMPLATE + self.PUT_RECORDS_TYPE_NAME.format(\
            domain = domain, type = record['type'], name = record['name'])
        self._put(url, json = record, headers = self._get_headers())
        logging.info('Updated record. Domain {} name {} type {}'.\
                     format(domain, record['name'], record['type']))

class BadResponse(Exception):
    def __init__(self, message, *args, **kwargs):
        self._message = message
        super(BadResponse, *args, **kwargs)

    def __str__(self, *args, **kwargs):
        return 'Response Data: {}'.format(self._message)
