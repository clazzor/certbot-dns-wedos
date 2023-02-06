#!/usr/bin/python3

import logging
import requests
from certbot.plugins.dns_common import DNSAuthenticator

logger = logging.getLogger(__name__)

class Authenticator(DNSAuthenticator):
    description = "Obtain certificates for Wedos dns servers."
    ttl = 60

    def __init__(self, *args: any, **kwargs: any) -> None:
        super(Authenticator, self).__init__(*args, **kwargs)
        self.credentials = None

    def more_info(self) -> str:
        return "This plugin configure a DNS TXT record to respond to a dns-01 challenge using the Hostpoint API"

    def prepare(self) -> None:
        logger.debug("Starting ..")

    def _setup_credentials(self) -> None:
        """self.credentials = self._configure_credentials(
            "credentials",
            "ISPConfig credentials INI file",
            {
                "endpoint": "URL of the ISPConfig Remote API.",
                "username": "Username for ISPConfig Remote API.",
                "password": "Password for ISPConfig Remote API.",
            },
        )"""
        pass

    def _perform(self, domain: str, validation_name: str, validation: str) -> None:
        print(f"data: {domain} -> {validation_name} \nKey: {validation}")

    def _cleanup(self, domain: str, validation_name: str, validation: str) -> None:
        pass
