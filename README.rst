godaddypy
==========
Python library useful for updating DNS settings through the GoDaddy v1 API (Updated as of 12/26/15)

Setup
--------

First go to https://developer.godaddy.com/keys/ and request a production API key.

Update your accounts.py file with the new key information...

.. code-block:: python

    accounts = [
        {
            'domains': [<domain to update>, ...],
            'api_key': '<your public key>',
            'api_secret': '<your secret key>'
        }
    ]


TODOs
--------

- Add more record support (currently only supports 'A' records)
- Make the code suck less (this is my first python script)