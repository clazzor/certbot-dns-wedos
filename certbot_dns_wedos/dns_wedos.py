"""Wedos DNS Authenticator plugin for Certbot"""

import hashlib
import re
import json
import logging
from datetime import datetime
from typing import Any, Callable, Optional

import pytz
import requests
from requests.exceptions import JSONDecodeError, RequestException

from certbot import errors
from certbot.plugins.dns_common import CredentialsConfiguration, DNSAuthenticator
from certbot_dns_wedos import URL, WEDOS_CODE, TTL

logger = logging.getLogger(__name__)

def convert_domain(func: Callable[..., Any]) -> Callable[..., Any]:
    def wrap(self, domain: str, validation_name: str, validation: str) -> Any:
        regex = r'([a-zA-Z0-9-]+)(\.[a-zA-Z]{2,5})?(\.[a-zA-Z]+$)'
        pure_domain = re.search(regex,  domain).group(0)
        sub_domain = re.sub(r'\.' + regex, '', validation_name)
        return func(self, pure_domain, sub_domain, validation)
    return wrap


class _WedosClient():
    def __init__(self, username: str, password: str) -> None:
        self.url = URL
        self.ttl = TTL
        self.username = username
        self.password = hashlib.sha1(password.encode('ascii')).hexdigest()
        self.session = requests.Session()

    def _find_txt_id(self, data: dict, validation: str) -> int:
        if 'data' not in data['response']:
            return -1
        if 'row' not in data['response']['data']:
            return -1
        data = data['response']['data']['row']

        for record in data:
            if 'rdata' not in record:
                continue
            if 'ID' not in record:
                continue
            if record['rdata'] == validation:
                return record['ID']
        return -1

    def _handler_wedos(self, response: requests.post) -> dict:
        data = {}
        try:
            data = response.json()
        except JSONDecodeError as err:
            raise errors.PluginError('Error occurred while parsing the response '
                                     f'from Wedos API into JSON format: {err}')
        if 'response' not in data:
            raise errors.PluginError('Unknown error occurred while receiving '
                                     'response from Wedos API.')
        if 'code' not in data['response']:
            raise errors.PluginError('Missing WAPI Error code in the '
                                     'response from Wedos API.')
        if data['response']['code'] >= 2000:
            raise errors.PluginError('Error code received from Wedos API, The error '
                                    f'code is {data["response"]["code"]}, '
                                    f'details {data["response"]}'
                                    f'you can find what the code mean here: {WEDOS_CODE}')
        return data

    def _handler_post(self, url: str, data: dict, headers: dict) -> dict:
        response = {}
        try:
            response = self.session.post(url, data=data, headers=headers, timeout=5)
            response.raise_for_status()
        except RequestException as err:
            raise errors.PluginError(f'Cannot access the Wedos API, Error: {err}')

        return self._handler_wedos(response)

    def client_send(self, command: str, requirement: dict = None) -> dict:
        time = datetime.now(pytz.timezone('Europe/Prague')).strftime('%H')
        auth = self.username + self.password + time
        auth = hashlib.sha1(auth.encode('ascii')).hexdigest()

        data = {
            'user': self.username,
            'auth': auth,
            'command': command,
            'data': requirement
        }

        data = {'request': json.dumps({'request': data})}
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        return self._handler_post(self.url, data, headers)

    @convert_domain
    def add_txt_record(self, domain: str, validation_name: str, validation: str) -> None:
        dns_row_add = {
            'domain': domain,
            'name': validation_name,
            'type': 'TXT',
            'ttl': self.ttl,
            'rdata': validation
        }

        self.client_send('dns-row-add', dns_row_add)
        self.client_send('dns-domain-commit', {'name': domain})

    @convert_domain
    def del_txt_record(self, domain: str, _validation_name: str, validation: str) -> None:
        dns_records = self.client_send('dns-rows-list', {'domain': domain})
        txt_id = self._find_txt_id(dns_records, validation)

        if txt_id == -1:
            logger.warning('Could not find the created TXT record. '
                           'It is recommended to check it.')
            return

        self.client_send('dns-row-delete', {'domain': domain, 'row_id': txt_id})
        self.client_send('dns-domain-commit', {'name': domain})


class Authenticator(DNSAuthenticator):
    description = 'Obtain certificates for Wedos dns servers.'
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.credentials: Optional[CredentialsConfiguration] = None

    @classmethod
    def add_parser_arguments(cls, add: Callable[..., None],
                             default_propagation_seconds: int = 450) -> None:
        super().add_parser_arguments(add, default_propagation_seconds)
        add('credentials', help='Wedos credentials INI file.')

    def more_info(self) -> str:
        return 'This plugin uses the Certbot DNS-01 challenge to create and delete' + \
            ' TXT records on the Wedos domain server using the Wedos API called' + \
            ' the WAPI. With this plugin, you can generate wildcard SSL certificates.'

    def _validate_credentials(self, credentials: CredentialsConfiguration) -> None:
        user = credentials.conf('user')
        auth = credentials.conf('auth')
        propagation_seconds = self.conf('propagation-seconds')

        if not user:
            raise errors.PluginError('Missing parameter USER (email) for the Wedos API.'
                                     ' [dns_wedos_user=john@example.com]')
        if not auth:
            raise errors.PluginError('Missing parameter AUTH (password) for the Wedos API.'
                                     ' [dns_wedos_auth=ExamplePassword]')
        if propagation_seconds < 300:
            raise errors.PluginError('Propagation seconds cannot be lower than 300 seconds.'
                                     ' (Recommended propagation time is 450 seconds)')
        if '@' not in user:
            raise errors.PluginError('Wrong parameter USER (email) for the Wedos API.')
        if len(auth) < 8:
            raise errors.PluginError('Wrong parameter AUTH (password) for the Wedos API.')

    def _setup_credentials(self) -> None:
        self.credentials = self._configure_credentials(
            'credentials',
            'Wedos Credentials INI file.',
            None,
            self._validate_credentials
        )

    def _perform(self, domain: str, validation_name: str, validation: str) -> None:
        self._get_wedos_client().add_txt_record(
            domain, validation_name, validation
        )

    def _cleanup(self, domain: str, validation_name: str, validation: str) -> None:
        self._get_wedos_client().del_txt_record(
            domain, validation_name, validation
        )

    def _get_wedos_client(self) -> _WedosClient:
        return _WedosClient(
            self.credentials.conf('user'),
            self.credentials.conf('auth')
        )
