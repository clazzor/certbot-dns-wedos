"""Wedos DNS plugin for Certbot.

This plugin uses the Certbot DNS-01 challenge to create and delete TXT
records on the Wedos domain server using the Wedos API called the WAPI. With
this plugin, you can generate wildcard SSL certificates.

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

# Wedos API
URL = 'https://api.wedos.com/wapi/json'
WEDOS_CODE = 'https://kb.wedos.global/wapi-codes/'
TIMEZONE = 'Europe/Prague'
WEDOS_ERROR_THRESHOLD = 2000

# HTTP client settings
HTTP_TIMEOUT = 15

# Validation settings
MIN_PASSWORD_LENGTH = 8
MIN_TTL = 300
DEFAULT_TTL = 300
MIN_PROPAGATION_SECONDS = 300
DEFAULT_PROPAGATION_SECONDS = 450
