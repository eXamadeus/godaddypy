import logging

import requests
from pif import get_public_ip

# Local imports
from accounts import accounts

_GET = 'GET'
_POST = 'POST'

_API_TEMPLATE = 'https://api.godaddy.com'

_GET_DOMAINS = '/v1/domains'
_GET_DOMAIN = '/v1/domains/{domain}'
_GET_RECORDS_TYPE_NAME = '/v1/domains/{domain}/records/{type}/@'
_PUT_RECORDS_TYPE_NAME = '/v1/domains/{domain}/records/{type}/{name}'
_PATCH_RECORDS = '/v1/domains/{domain}/records'
_PUT_RECORDS = '/v1/domains/{domain}/records'


def discover_domains(account):
    url = _API_TEMPLATE + _GET_DOMAINS
    resp = requests.get(url, headers=get_auth_headers(account))
    data = resp.json()

    log_response_from_method('get', discover_domains.__name__, resp)

    domains = list()
    for item in data:
        domain = item['domain']
        if item['status'] == 'ACTIVE':
            domains.append(domain)
            display_and_log('Discovered domains: {}'.format(domain))

    return domains


def display_and_log(message):
    print(message)
    logging.info(message)


def get_auth_headers(account):
    _sso_key_template = 'sso-key {api_key}:{api_secret}'

    return {'Authorization': _sso_key_template.format(api_key=account['api_key'], api_secret=account['api_secret'])}


def get_domain_info(account, domain):
    url = _API_TEMPLATE + _GET_DOMAIN.format(domain=domain)
    resp = requests.get(url, headers=get_auth_headers(account))
    data = resp.json()
    log_response_from_method('get', get_domain_info.__name__, resp)

    return data


def get_domain_a_records(account, domain):
    url = _API_TEMPLATE + _GET_RECORDS_TYPE_NAME.format(domain=domain, type='A')
    resp = requests.get(url, headers=get_auth_headers(account))
    data = resp.json()

    log_response_from_method('get', get_domain_a_records.__name__, resp)
    display_and_log('Retrieved {} records from {}.'.format(len(data), domain))

    return data


def log_response_from_method(req_type, func_name, resp):
    logging.info('[{req_type}] {func_name} response: {resp}'.format(func_name=func_name, resp=resp,
                                                                    req_type=req_type.upper()))


def put_new_a_records(account, domain, records):
    url = _API_TEMPLATE + _PUT_RECORDS_TYPE_NAME.format(domain=domain, type='A', name='@')

    headers = get_auth_headers(account)

    resp = requests.put(url, json=records, headers=headers)
    log_response_from_method('put', put_new_a_records.__name__, resp)

    if resp.status_code == 200:
        display_and_log('Updated {} records @ {}'.format(len(records), domain))


def remove_key_from_dict(dictionary, key_to_remove):
    return {key: value for key, value in dictionary.items() if key != key_to_remove}


def update_records_for_account(account, public_ip):
    for domain in discover_domains(account):
        records = get_domain_a_records(account, domain)

        for record in records:
            data = {'data': public_ip}
            record.update(data)

        put_new_a_records(account, domain, records)


def main():
    public_ip = get_public_ip()
    display_and_log('Public IP: {}'.format(public_ip))

    for account in accounts:
        display_and_log('Updating account with API_KEY: {}'.format(account['api_key']))
        update_records_for_account(account, public_ip)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, filename='godaddypy.log')
    main()
