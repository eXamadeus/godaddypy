__all__ = ['Account']


class Account(object):
    """The GoDaddyPy Account.

    An account is used to provide authentication headers to the `godaddypy.Client`.
    """
    _api_key = None
    _api_secret = None

    _SSO_KEY_TEMPLATE = 'sso-key {api_key}:{api_secret}'

    def __init__(self, api_key, api_secret):
        """Create a new `godadypy.Account` object.

        :type api_key: str
        :param api_key: The API_KEY provided by GoDaddy

        :type api_secret: str
        :param api_secret: The API_SECRET provided by GoDaddy
        """

        self._api_key = api_key
        self._api_secret = api_secret

    def get_auth_headers(self):
        return {
            'Authorization': self._SSO_KEY_TEMPLATE.format(api_key=self._api_key,
                                                           api_secret=self._api_secret)}
