GoDaddyPy
==========
Python library useful for updating DNS settings through the GoDaddy v1 API (Updated as of 12/26/15).

This concept was spawned from pygodaddy @ https://github.com/observerss/pygodaddy.

Setup
--------

First, go to https://developer.godaddy.com/keys/ and request a production API key and secret.

*Note: Sometimes the production API keys don't seem to work correctly.  Just delete it and request another one.*

Second, install GoDaddyPy with pip.

.. code-block:: bash

    $ pip install godaddypy

..

Examples
--------

.. code-block:: python

    >>> from godaddypy import Client, Account
    >>>
    >>> my_acct = Account(api_key='PUBLIC_KEY', api_secret='SECRET_KEY')
    >>> client = Client(my_acct)
    >>>
    >>> client.get_domains()
    ['abc.com', '123.info']
    >>>
    >>> client.get_a_records('abc.com')
    [{'name': '@', 'ttl': 3600, 'data': '255.255.255.255', 'type': 'A'}]
    >>>
    >>> client.update_ip('1.1.1.1', domains=['abc.com'])
    >>>
    >>> client.get_a_records('abc.com')
    [{'name': '@', 'ttl': 3600, 'data': '1.1.1.1', 'type': 'A'}]
..

TODOs
--------

- Add more record support (currently only supports 'A' records)
- Make the code suck less (this is my first time writing python)
- Add unit testing
