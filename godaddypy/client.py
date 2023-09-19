from __future__ import unicode_literals

import logging
from enum import Enum

import requests

try:
    # python3.x
    from urllib.parse import urljoin
except ImportError:
    # python2.x
    # noinspection PyUnresolvedReferences
    from urlparse import urljoin

__all__ = ["Client", "BadResponse"]

GODADDY_API_BASE_URL = "https://api.godaddy.com/"
GODADDY_API_VERSION = "v1"


class Client(object):
    """The GoDaddyPy Client.

    This client is used to connect to the GoDaddy API and to perform requests with said API.
    """

    class Domain(Enum):
        AUTH_CODE = "authCode"
        CONTACTS = "contacts"
        NAME_SERVERS = "nameServers"

    def __init__(
        self,
        account,
        log_level=None,
        api_base_url=GODADDY_API_BASE_URL,
        api_version=GODADDY_API_VERSION,
    ):
        """Create a new `godaddypy.Client` object

        :type account: godaddypy.Account
        :param account: The godaddypy.Account object to create auth headers with.
        """

        # Logging setup
        self.logger = logging.getLogger("GoDaddyPy.Client")
        # Explicit override of logging level
        if log_level is not None:
            self.logger.setLevel(log_level)

        # Templates
        self.API_TEMPLATE = urljoin(api_base_url, api_version)
        self.DOMAINS = "/domains"
        self.DOMAIN_INFO = "/domains/{domain}"
        self.RECORDS = "/domains/{domain}/records"
        self.RECORDS_TYPE = "/domains/{domain}/records/{type}"
        self.RECORDS_TYPE_NAME = "/domains/{domain}/records/{type}/{name}"

        self.account = account

    def _build_record_url(self, domain, record_type=None, name=None):
        url = self.API_TEMPLATE

        if name is None and record_type is None:
            url += self.RECORDS.format(domain=domain)
        elif name is None and record_type is not None:
            url += self.RECORDS_TYPE.format(domain=domain, type=record_type)
        elif name is not None and record_type is None:
            raise ValueError("If name is specified, type must also be specified")
        else:
            url += self.RECORDS_TYPE_NAME.format(domain=domain, type=record_type, name=name)

        return url

    def _get_headers(self):
        return self.account.get_headers()

    def _get_json_from_response(self, url, json=None, **kwargs):
        return self._request_submit(requests.get, url=url, json=json, **kwargs).json()

    def _log_response_from_method(self, req_type, resp):
        self.logger.debug("[{req_type}] response: {resp}".format(resp=resp, req_type=req_type.upper()))
        self.logger.debug("Response data: {}".format(resp.content))

    def _patch(self, url, json=None, **kwargs):
        return self._request_submit(requests.patch, url=url, json=json, **kwargs)

    def _put(self, url, json=None, **kwargs):
        return self._request_submit(requests.put, url=url, json=json, **kwargs)

    def _delete(self, url, json=None, **kwargs):
        return self._request_submit(requests.delete, url=url, json=json, **kwargs)

    def _request_submit(self, func, **kwargs):
        """A helper function that will wrap any requests we make.

        :param func: a function reference to the requests method to invoke
        :param kwargs: any extra arguments that requests.request takes

        :type func: (url: Any, data: Any, json: Any, kwargs: Dict)
        """
        resp = func(headers=self._get_headers(), **kwargs)
        self._log_response_from_method(func.__name__, resp)
        self._validate_response_success(resp)
        return resp

    @staticmethod
    def _validate_response_success(response):
        """Only raise exceptions for 4xx/5xx errors because GoDaddy doesn't
        always return 200 for a correct request"""
        try:
            response.raise_for_status()
        except Exception:
            raise BadResponse(response.json())

    def add_record(self, domain, record):
        """Adds the specified DNS record to a domain.

        :param domain: the domain to add the record to
        :param record: the record to add
        """
        self.add_records(domain, [record])

        # If we didn't get any exceptions, return True to let the user know
        return True

    def add_records(self, domain, records):
        """Adds the specified DNS records to a domain.

        :param domain: the domain to add the records to
        :param records: the records to add
        """
        url = self.API_TEMPLATE + self.RECORDS.format(domain=domain)
        self._patch(url, json=records)
        self.logger.debug("Added records @ {}".format(records))

        # If we didn't get any exceptions, return True to let the user know
        return True

    def get_domain_info(self, domain):
        """Get the GoDaddy supplied information about a specific domain.

        :param domain: The domain to obtain info about.
        :type domain: str

        :return A JSON string representing the domain information
        """
        url = self.API_TEMPLATE + self.DOMAIN_INFO.format(domain=domain)
        return self._get_json_from_response(url)

    def get_domains(self, limit=1000, marker=None, **params):
        """Returns a list of domains for the authenticated user.

        :param limit: maximum number of domains to return (max: 1000)
        :param marker: marker domain to use as offset in results
        :param params:   Dict of query params to send with the domains request
        """
        url = self.API_TEMPLATE + self.DOMAINS
        params["limit"] = limit
        if marker:
            params["marker"] = marker
        data = self._get_json_from_response(url, params=params)
        domains = list()
        for item in data:
            domain = item["domain"]
            domains.append(domain)
            self.logger.debug("Discovered domains: {}".format(domain))

        return domains

    def update_domain(self, domain, **kwargs):
        """
         Update an existing domain via PATCH /v1/domains/{domain}
         https://developer.godaddy.com/doc#!/_v1_domains/update

         currently it supports ( all optional )
            locked = boolean
            nameServers = list
            renewAuto = boolean
            subaccountId = string

        NOTE: It can take minutes for GoDaddy to update the record.  Make sure you
        wait before checking status.
        """
        update = {}
        for k, v in kwargs.items():
            update[k] = v
        url = self.API_TEMPLATE + self.DOMAIN_INFO.format(domain=domain)
        self._patch(url, json=update)
        self.logger.info("Updated domain {} with {}".format(domain, update))

    def get_records(self, domain, record_type=None, name=None, offset=1, limit=500):
        """Returns records from a single domain.  You can specify type/name as filters for the records returned.  If
        you specify a name you MUST also specify a type.

        :param domain: the domain to get DNS information from
        :param record_type: the type of record(s) to retrieve
        :param name: the name of the record(s) to retrieve
        :param offset: result page offset (starting at 1)
        :param limit: maximum number of elements to return (max: 500)
        """

        url = self._build_record_url(domain, record_type=record_type, name=name)
        data = self._get_json_from_response(url, params=dict(limit=limit, offset=offset))
        self.logger.debug("Retrieved {} record(s) from {}.".format(len(data), domain))

        return data

    def replace_records(self, domain, records, record_type=None, name=None):
        """This will replace all records at the domain.  Record type and record name can be provided to filter
        which records to replace.

        :param domain: the domain to replace records at
        :param records: the records you will be saving
        :param record_type: the type of records you want to replace (eg. only replace 'A' records)
        :param name: the name of records you want to replace (eg. only replace records with name 'test')

        :return: True if no exceptions occurred
        """

        url = self._build_record_url(domain, name=name, record_type=record_type)
        self._put(url, json=records)

        # If we didn't get any exceptions, return True to let the user know
        return True

    def update_ip(self, ip, record_type="A", domains=None, subdomains=None):
        """Update the IP address in all records, specified by type, to the value of ip.  Returns True if no
        exceptions occurred during the update.  If no domains are provided, all domains returned from
        self.get_domains() will be updated.  By default, only A records are updated.

        :param record_type: The type of records to update (eg. 'A')
        :param ip: The new IP address (eg. '123.1.2.255')
        :param domains: A list of the domains you want to update (eg. ['123.com','abc.net'])
        :param subdomains: A list of the subdomains you want to update (eg. ['www','dev'])

        :type record_type: str or unicode
        :type ip: str or unicode
        :type domains: str, list of str
        :type subdomains: str, list of str

        :return: True if no exceptions occurred
        """

        if domains is None:
            domains = self.get_domains()
        elif isinstance(domains, str):
            domains = [domains]
        else:
            # we have a tuple, set, or something else, try to convert it to a list
            domains = list(domains)

        for domain in domains:
            a_records = self.get_records(domain, record_type=record_type)
            for record in a_records:
                r_name = str(record["name"])
                r_ip = str(record["data"])

                if not r_ip == ip:
                    # noinspection PyUnresolvedReferences
                    if (
                        subdomains is None
                        or (isinstance(subdomains, str) and r_name == subdomains)
                        or r_name in subdomains
                    ):
                        record.update(data=str(ip))
                        self.update_record(domain, record)

        # If we didn't get any exceptions, return True to let the user know
        return True

    def delete_records(self, domain, name, record_type="A"):
        """Deletes records by name and type

        :param domain: the domain to delete records from
        :param name: the name of records to remove
        :param record_type: the type of records to remove

        :return: True if no exceptions occurred
        """
        url = self._build_record_url(domain=domain, record_type=record_type, name=name)
        self._delete(url=url)

        # If we didn't get any exceptions, return True to let the user know
        return True

    def update_record(self, domain, record, record_type=None, name=None):
        """Call to GoDaddy API to update a single DNS record

        :param name: only required if the record is None (deletion)
        :param record_type: only required if the record is None (deletion)
        :param domain: the domain where the DNS belongs to (eg. 'example.com')
        :param record: dict with record info (ex. {'name': 'dynamic', 'ttl': 3600, 'data': '1.1.1.1', 'type': 'A'})

        :return: True if no exceptions occurred
        """
        if record_type is None:
            record_type = record["type"]
        if name is None:
            name = record["name"]

        url = self.API_TEMPLATE + self.RECORDS_TYPE_NAME.format(domain=domain, type=record_type, name=name)
        self._put(url, json=[record])
        self.logger.info(
            "Updated record. Domain {} name {} type {}".format(domain, str(record["name"]), str(record["type"]))
        )

        # If we didn't get any exceptions, return True to let the user know
        return True

    def update_record_ip(self, ip, domain, name, record_type):
        """Update the IP address(es) for (a) domain(s) specified by type and name.

        :param ip: the new IP for the DNS record (ex. '123.1.2.255')
        :param domain: the domain where the DNS belongs to (ex. 'example.com')
        :param name: the DNS record name to be updated (ex. 'dynamic')
        :param record_type: Record type (ex. 'CNAME', 'A'...)

        :return: True if no exceptions occurred
        """

        records = self.get_records(domain, name=name, record_type=record_type)
        data = {"data": str(ip)}
        for rec in records:
            rec.update(data)
            self.update_record(domain, rec)

        # If we didn't get any exceptions, return True to let the user know
        return True


class BadResponse(Exception):
    def __init__(self, message, *args, **kwargs):
        self.message = message
        super(BadResponse, *args, **kwargs)

    def __str__(self, *args, **kwargs):
        return "Response Data: {}".format(self.message)
