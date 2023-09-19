#!/usr/bin/env python3

# Full package imports
import sys
import pif

# Partial imports
from godaddypy import Client, Account
from godaddypy.client import BadResponse

domain = "example.com"
a_record = "www"

userAccount = Account(api_key="YOUR_KEY", api_secret="YOUR_SECRET")
userClient = Client(userAccount)
publicIP = pif.get_public_ip("ident.me")

try:
    records = userClient.get_records(domain, name=a_record, record_type="A")
    for record in records:
        if publicIP != record["data"]:
            updateResult = userClient.update_record_ip(publicIP, domain, a_record, "A")
            if updateResult is True:
                print("Update ended with no Exception.")
        else:
            print("No DNS update needed.")
except ValueError | BadResponse as e:
    print(e)
    sys.exit()
