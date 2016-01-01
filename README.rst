GoDaddyPy
==========
Python library useful for updating DNS settings through the GoDaddy v1 API (Updated as of 12/26/15).

This concept was spawned from pygodaddy @ https://github.com/observerss/pygodaddy.

Requirements
--------

The `requests` library is required for GoDaddyPy.  `pip` will handle the installation.

Setup
--------

First, go to https://developer.godaddy.com/keys/ and request a production API key and secret.

Second, install GoDaddyPy with pip.

.. code-block:: bash

    $ pip install godaddypy

..

Examples
--------

.. code-block:: python

    >>> from godaddypy import Account, GoDaddyClient
    >>> my_acct = Account(api_key='PUBLIC_KEY', api_secret='SECRET_KEY')
    >>>
    >>> client = GoDaddyClient(my_acct)
    >>> client.get_domains()
    ['abc.com', '123.info']
    >>> client.get_a_records(client.get_domains()[0])
    [{'type': 'A', 'name': '@', 'ttl': 3600, 'data': '255.255.255.255'}]
    >>>
..

TODOs
--------

- Add more record support (currently only supports 'A' records)
- Make the code suck less (this is my first python script)
- Add unit testing