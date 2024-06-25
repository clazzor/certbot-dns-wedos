import hashlib 
import pytz
from datetime import datetime

import requests
from json import dumps
from typing import Any, Callable, Optional

import logging
from certbot import errors
from certbot.plugins.dns_common import CredentialsConfiguration, DNSAuthenticator

logger = logging.getLogger(__name__)
URL = 'https://api.wedos.com/wapi/json'

class _WedosClient():
    def __init__(self, username: str, password: str) -> None:
        self.url = URL
        self.username = username
        self.password = password
        self.session = requests.Session()

    def _findID(self, data: dict, key: str) -> int:
        ID = -1
        try:
            for row in data['data']['row']:
                if row['rdata'] == key:
                    ID = row['ID']
                    break
            return ID
        except:
            return ID
        
    def _validResponse(self, response: requests.post) -> None:
        if not response.ok:
            raise errors.PluginError('Cannot access the Wedos API, '
                                    f'HTTP error code is {response.status_code}')
        try:
            responseJson = response.json()
        except Exception as e:
            raise errors.PluginError('Error occurred while parsing the response '
                                     f'from Wedos API into JSON format: {e}')
        if 'response' not in responseJson:
            raise errors.PluginError('Unknown error occurred while receiving '
                                     'response from Wedos API.')
        if 'code' not in responseJson['response']:
            raise errors.PluginError('Missing WAPI Error code in the '
                                     'response from Wedos API.')
        if responseJson['response']['code'] >= 2000:
            raise errors.PluginError('Error code received from Wedos API, The error '
                                    f'code is  {responseJson["response"]["code"]}')
        
    def _clientSend(self, command: str, requirement: dict = None) -> requests.post:
        password = hashlib.sha1(self.password.encode('ascii')).hexdigest()
        time = datetime.now(pytz.timezone('Europe/Prague')).strftime('%H')
        auth = self.username + password + time
        auth = hashlib.sha1(auth.encode('ascii')).hexdigest()

        data = {
            'user': self.username,
            'auth': auth,
            'command': command,
            'data': requirement
        }
            
        data = {'request': dumps({'request': data})}
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        response = self.session.post(self.url, data=data, headers=headers)

        self._validResponse(response)
        return response

    def add_txt_record(self, domain: str, validation_name: str, validation: str) -> None:
        dns_row_add = {
            'domain': domain,
            'name': validation_name.replace('.' + domain, ''),
            'type': 'TXT',
            'ttl': 300,
            'rdata': validation
        }

        self._clientSend('dns-row-add', dns_row_add)
        self._clientSend('dns-domain-commit', {'name': domain})

    def del_txt_record(self, domain: str, validation_name: str, validation: str) -> None:
        response = self._clientSend('dns-rows-list', {'domain': domain})
        id = self._findID(response.json()['response'],  validation)
        if id == -1:
            logger.warn('Could not find the created TXT record. It is recommended to check it.')
            return

        self._clientSend('dns-row-delete', {'domain': domain, 'row_id': id})
        self._clientSend('dns-domain-commit', {'name': domain})


class Authenticator(DNSAuthenticator):
    description = 'Obtain certificates for Wedos dns servers.'
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.credentials: Optional[CredentialsConfiguration] = None

    @classmethod
    def add_parser_arguments(cls, add: Callable[..., None],
                             default_propagation_seconds: int = 360) -> None:
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
                                     ' (Recommended propagation time is 420 seconds)')

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