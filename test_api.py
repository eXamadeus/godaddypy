import requests

from .accounts import accounts

url = 'https://api.godaddy.com/v1/domains/juliancoy.com'

h_test = {
    'Authorization': 'sso-key ' + accounts[0]['API_KEY'] + ':' + accounts[0]['API_SECRET']
}

h_sid = {
    "X-Shopper-Id": "70838100"
}

r_test = requests.get(url, headers=h_test)

print '==TEST=='

print 'Headers:', h_test
print 'URL:', r_test.url
print '\t', r_test
print '\t', r_test.text
