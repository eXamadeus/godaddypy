.. image:: https://travis-ci.org/eXamadeus/godaddypy.svg?branch=master
    :target: https://travis-ci.org/eXamadeus/godaddypy

GoDaddyPy
==========
Python library useful for updating DNS settings through the GoDaddy v1 API.

Source located @ https://github.com/eXamadeus/godaddypy

This concept was spawned from observerss' pygodaddy @ https://github.com/observerss/pygodaddy.

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
    ['domain1.example', 'domain2.example']
    >>>
    >>> client.get_a_records('domain1.example')
    [{'name': 'dynamic', 'ttl': 3600, 'data': '1.1.1.1', 'type': 'A'}]
    >>>
    >>> client.update_ip('2.2.2.2', domains=['domain1.example'])
    >>>
    >>> client.get_a_records('domain1.example')
    [{'name': 'dynamic', 'ttl': 3600, 'data': '2.2.2.2', 'type': 'A'}]
    >>>
    >>> client.get_record('domain1.example', 'dynamic', 'A')
    {'name': 'dynamic', 'ttl': 3600, 'data': '2.2.2.2', 'type': 'A'}
    >>>
    >>> client.update_record_ip('3.3.3.3', 'domain1.example', 'dynamic', 'A')
    >>>
    >>> client.get_record('domain1.example', 'dynamic', 'A')
    {'name': 'dynamic', 'ttl': 3600, 'data': '3.3.3.3', 'type': 'A'}
..

TODOs
--------

- Add more record support (currently only supports 'A' records)
- Make the code suck less (this is my first time writing python)
- Add unit testing
