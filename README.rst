godaddypy
==========
Python library useful for updating DNS settings through the GoDaddy v1 API (Updated as of 12/26/15)

Setup
--------

First go to https://developer.godaddy.com/keys/ and request a production API key and secret.

Example
--------


.. code-block:: python

    >>> from godaddypy import Account, GoDaddyAPI
    >>> my_acct = Account('PUBLIC_KEY','SECRET_KEY')
    >>>
    >>> client = GoDaddyAPI(my_acct)
    >>> client.get_domains()
    ['abc.com', '123.info']
    >>>
..

TODOs
--------

- Add more record support (currently only supports 'A' records)
- Make the code suck less (this is my first python script)