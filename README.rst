|downloads| |climate|

GoDaddyPy
=========

Python library useful for updating DNS settings through the GoDaddy v1
API.

-  PyPI: https://pypi.org/project/GoDaddyPy/
-  Source: https://github.com/eXamadeus/godaddypy
-  Migrated from: https://github.com/eXamadeus-zz/godaddypy
-  Concept originated from observerss' pygodaddy @ https://github.com/observerss/pygodaddy.

Setup
-----

First, go to https://developer.godaddy.com/keys/ and request a production API key and secret.

*Note: Sometimes the production API keys don't seem to work correctly. Just delete it and request another one.*

Second, install GoDaddyPy with pip.

.. code:: bash

   $ pip install godaddypy

GoDaddyPy supports three methods for providing your credentials to the library, which are honored in the following order:

1. Passing them directly to the Account object
2. Setting the GODADDY_API_KEY and GODADDY_API_SECRET environment
   variables
3. Storing them in a credentials.yml file

For convenience, a configuration tool has been provided that can be run from your terminal or in Python. This tool will
prompt for your API key and secret, and store them in a config file in your home directory following the XDG Base
Directory specification. I have only tested this on Mac, but it should also work on Linux. I recommend env vars for
Windows and/or CI/CD.

.. code:: bash

   $ python -m godaddypy

.. code:: python

   >>> from godaddypy import Account
   >>> acct = Account.configure()
   Enter GoDaddy API Key [None]: example_key
   Enter GoDaddy API Secret [None]: example_secret
   >>> account = Account()
   >>> account._config
   Configuration(key='example_key', secret='example_secret')

Examples
--------

Also see /examples for more examples.

.. code:: python

   >>> from godaddypy import Client, Account
   >>>
   >>> my_acct = Account(api_key='PUBLIC_KEY', api_secret='SECRET_KEY')
   >>> client = Client(my_acct)
   >>>
   >>> # Or if you want to use a delegate...
   >>> delegate_acct = Account(api_key='PUBLIC_KEY', api_secret='SECRET_KEY', delegate='DELEGATE_ID')
   >>> delegate_client = Client(delegate_acct)
   >>>
   >>> client.get_domains()
   ['domain1.example', 'domain2.example']
   >>>
   >>> client.get_records('domain1.example', record_type='A')
   [{'name': 'dynamic', 'ttl': 3600, 'data': '1.1.1.1', 'type': 'A'}]
   >>>
   >>> client.update_ip('2.2.2.2', domains=['domain1.example'])
   True
   >>>
   >>> client.get_records('domain1.example')
   [{'name': 'dynamic', 'ttl': 3600, 'data': '2.2.2.2', 'type': 'A'}, {'name': 'dynamic', 'ttl': 3600, 'data': '::1',
   'type': 'AAAA'},]
   >>>
   >>> client.get_records('apple.com', record_type='A', name='@')
   [{u'data': u'1.2.3.4', u'type': u'A', u'name': u'@', u'ttl': 3600}]
   >>>
   >>> client.update_record_ip('3.3.3.3', 'domain1.example', 'dynamic', 'A')
   True
   >>>
   >>> client.add_record('apple.com', {'data':'1.2.3.4','name':'test','ttl':3600, 'type':'A'})
   True
   >>>
   >>> client.delete_records('apple.com', name='test')
   True

Contributing
------------

If you want to contribute, first off: thank you! Second, please check out the Contributing Guidelines,
`CONTRIBUTING <https://github.com/eXamadeus/godaddypy/blob/main/CONTRIBUTING.md>`__.

Steps to Contribute
~~~~~~~~~~~~~~~~~~~

1. Pull the repository
2. Run make install to install the library and development dependencies
3. Make changes
4. Add tests
5. Open a pull request towards the main branch

.. |downloads| image:: https://img.shields.io/pypi/dm/godaddypy.svg
   :target: https://pypi.python.org/pypi/godaddypy
.. |climate| image:: https://codeclimate.com/github/eXamadeus/godaddypy/badges/gpa.svg
   :target: https://codeclimate.com/github/eXamadeus/godaddypy
