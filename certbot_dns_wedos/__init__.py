"""
This plugin uses the Certbot DNS-01 challenge to create and delete
TXT records on the Wedos domain server using the Wedos API called
the WAPI. With this plugin, you can generate wildcard SSL certificates.

Basic usage:
 certbot certonly --authenticator dns-wedos \
 --dns-wedos-propagation-seconds 450 \
 --dns-wedos-credentials /path/to/the/file.ini \
 -d example.com -d *.example.com

Basic file.ini example:
 dns_wedos_user=user@example.com
 dns_wedos_auth=examplepassword

GitHub: https://github.com/clazzor/certbot-dns-wedos/
"""

URL = 'https://api.wedos.com/wapi/json'
WEDOS_CODE = 'https://kb.wedos.com/en/wapi-api-interface/wapi-manual/#return-codes'
TTL = 300
