"""Wedos DNS Authenticator plugin for Certbot."""

import hashlib
import json
import logging
from collections.abc import Callable
from datetime import datetime
from typing import Any

import pytz
import requests
import tldextract
from certbot import errors
from certbot.plugins.dns_common import CredentialsConfiguration, DNSAuthenticator
from requests.exceptions import JSONDecodeError, RequestException

from certbot_dns_wedos import (
    DEFAULT_PROPAGATION_SECONDS,
    DEFAULT_TTL,
    HTTP_TIMEOUT,
    MIN_PASSWORD_LENGTH,
    MIN_PROPAGATION_SECONDS,
    MIN_TTL,
    TIMEZONE,
    URL,
    WEDOS_CODE,
    WEDOS_ERROR_THRESHOLD,
)

logger = logging.getLogger(__name__)


def convert_domain(func: Callable[..., Any]) -> Callable[..., Any]:
    def wrap(self: object, domain: str, validation_name: str, validation: str) -> Any:
        extracted = tldextract.extract(domain)
        pure_domain = f'{extracted.domain}.{extracted.suffix}'
        sub_domain = validation_name

        if validation_name.endswith(f'.{pure_domain}'):
            sub_domain = validation_name[: -len(pure_domain) - 1]

        return func(self, pure_domain, sub_domain, validation)

    return wrap


class WedosClient:
    def __init__(self, username: str, password: str, ttl: int) -> None:
        self.url = URL
        self.ttl = ttl
        self.username = username.strip()
        self.password = hashlib.sha1(password.encode('utf-8')).hexdigest()
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
                return int(record['ID'])
        return -1

    def _handler_wedos(self, response: requests.Response) -> dict:
        data = {}
        try:
            data = response.json()
        except JSONDecodeError as err:
            raise errors.PluginError(
                'Error occurred while parsing the response '
                f'from Wedos API into JSON format: {err}'
            ) from err
        if 'response' not in data:
            raise errors.PluginError(
                'Unknown error occurred while receiving response from Wedos API.'
            )
        if 'code' not in data['response']:
            raise errors.PluginError(
                'Missing WAPI Error code in the response from Wedos API.'
            )
        try:
            code = int(data['response']['code'])
        except ValueError as err:
            raise errors.PluginError(
                'Invalid response code format from Wedos API: '
                f'{data["response"]["code"]}'
            ) from err

        if code >= WEDOS_ERROR_THRESHOLD:
            raise errors.PluginError(
                f'Error code received from Wedos API: {data["response"]["code"]}. '
                f'Details: {data["response"]}. '
                f'You can find what the code means here: {WEDOS_CODE}'
            )
        return data

    def _handler_post(self, url: str, data: dict, headers: dict) -> dict:
        response = {}
        try:
            response = self.session.post(
                url,
                data=data,
                headers=headers,
                timeout=HTTP_TIMEOUT,
            )
            response.raise_for_status()
        except RequestException as err:
            raise errors.PluginError(
                f'Cannot access the Wedos API, Error: {err}'
            ) from err

        return self._handler_wedos(response)

    def client_send(self, command: str, requirement: dict | None = None) -> dict:
        time = datetime.now(pytz.timezone(TIMEZONE)).strftime('%H')
        auth = self.username + self.password + time
        auth = hashlib.sha1(auth.encode('utf-8')).hexdigest()

        data = {
            'user': self.username,
            'auth': auth,
            'command': command,
            'data': requirement,
        }

        data = {'request': json.dumps({'request': data})}
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        return self._handler_post(self.url, data, headers)

    @convert_domain
    def add_txt_record(
        self,
        domain: str,
        validation_name: str,
        validation: str,
    ) -> None:
        dns_row_add = {
            'domain': domain,
            'name': validation_name,
            'type': 'TXT',
            'ttl': self.ttl,
            'rdata': validation,
        }

        self.client_send('dns-row-add', dns_row_add)
        self.client_send('dns-domain-commit', {'name': domain})

    @convert_domain
    def del_txt_record(
        self,
        domain: str,
        _validation_name: str,
        validation: str,
    ) -> None:
        dns_records = self.client_send('dns-rows-list', {'domain': domain})
        txt_id = self._find_txt_id(dns_records, validation)

        if txt_id == -1:
            logger.warning(
                'Could not find the created TXT record. It is recommended to check it.'
            )
            return

        self.client_send('dns-row-delete', {'domain': domain, 'row_id': txt_id})
        self.client_send('dns-domain-commit', {'name': domain})


class Authenticator(DNSAuthenticator):
    description = 'Obtain certificates for Wedos dns servers.'

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.credentials: CredentialsConfiguration | None = None

    @classmethod
    def add_parser_arguments(
        cls,
        add: Callable[..., None],
        default_propagation_seconds: int = DEFAULT_PROPAGATION_SECONDS,
    ) -> None:
        super().add_parser_arguments(add, default_propagation_seconds)
        add('credentials', help='Wedos credentials INI file.')

    def more_info(self) -> str:
        return (
            'This plugin uses the Certbot DNS-01 challenge to create and delete '
            'TXT records on the Wedos domain server using the Wedos API called '
            'the WAPI. With this plugin, you can generate wildcard SSL certificates.'
        )

    def _validate_credentials(self, credentials: CredentialsConfiguration) -> None:
        user = credentials.conf('user')
        auth = credentials.conf('auth')
        ttl = credentials.conf('ttl')
        propagation_seconds = self.conf('propagation-seconds')

        if not user:
            raise errors.PluginError(
                'Missing parameter USER (email) for the Wedos API. '
                '[dns_wedos_user=john@example.com]'
            )
        if not auth:
            raise errors.PluginError(
                'Missing parameter AUTH (password) for the Wedos API. '
                '[dns_wedos_auth=ExamplePassword]'
            )
        if propagation_seconds < MIN_PROPAGATION_SECONDS:
            raise errors.PluginError(
                'Propagation seconds cannot be less than '
                f'{MIN_PROPAGATION_SECONDS} seconds. '
                '(Recommended propagation time is '
                f'{DEFAULT_PROPAGATION_SECONDS} seconds)'
            )
        if ttl and (not ttl.isnumeric() or int(ttl) < MIN_TTL):
            raise errors.PluginError(
                f'TTL must be an integer and at least {MIN_TTL} seconds.'
            )
        if '@' not in user:
            raise errors.PluginError('Wrong parameter USER (email) for the Wedos API.')
        if len(auth) < MIN_PASSWORD_LENGTH:
            raise errors.PluginError(
                'Wrong parameter AUTH (password) for the Wedos API.'
            )

    def _setup_credentials(self) -> None:
        self.credentials = self._configure_credentials(
            'credentials',
            'Wedos Credentials INI file.',
            None,
            self._validate_credentials,
        )

    def _perform(self, domain: str, validation_name: str, validation: str) -> None:
        self._get_wedos_client().add_txt_record(domain, validation_name, validation)

    def _cleanup(self, domain: str, validation_name: str, validation: str) -> None:
        self._get_wedos_client().del_txt_record(domain, validation_name, validation)

    def _get_wedos_client(self) -> WedosClient:
        if not hasattr(self, '_client_instance'):
            self._client_instance = WedosClient(
                self.credentials.conf('user'),
                self.credentials.conf('auth'),
                int(self.credentials.conf('ttl') or DEFAULT_TTL),
            )
        return self._client_instance
