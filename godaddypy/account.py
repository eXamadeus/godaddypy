import logging

_logger = logging.getLogger(__name__)

__all__ = ['Account']


class Account(object):
    _api_key = None
    _api_secret = None

    _SSO_KEY_TEMPLATE = 'sso-key {api_key}:{api_secret}'

    def __init__(self, api_key, api_secret):
        self._api_key = api_key
        self._api_secret = api_secret

    def get_auth_headers(self):
        return {
            'Authorization': self._SSO_KEY_TEMPLATE.format(api_key=self._api_key,
                                                           api_secret=self._api_secret)}
