#!/usr/bin/python3

import logging, requests, json, hashlib, time
from datetime import datetime
from certbot.plugins.dns_common import DNSAuthenticator
from certbot import errors
logger = logging.getLogger(__name__)

URL = "https://api.wedos.com/wapi/json"
TTL = 300

class _WedosClient():

    def __init__(self, username: str, password: str) -> None:
        self.url = URL
        self.username = username
        self.password = password
        self.ttl = TTL
        self.session = requests.Session()


    def _getHour() -> str:
        time = str(datetime.now().hour)
        if len(time) == 1: time = "0" + time
        return time


    def _clientConnect(self, command: str, params: dict = None) -> requests.post:
        time = str(datetime.now().hour)
        if len(time) == 1: time = "0" + time

        auth = (self.username + self.password + time ).encode("ascii")
        data = {
            "user": self.username,
            "auth": hashlib.sha1(auth).hexdigest(),
            "command": command
            }

        if type(params) is dict: data.update({"data": params})
        data = json.dumps({"request": data})
        response = self.session.post(self.url, data={'request': data})

        if not response.ok:
            raise errors.PluginError(f"Cannot access Api Wedos, HTTP error code is {response.status_code}")

        if response.json()["response"]["code"] >= 2000:
            raise errors.PluginError(f"Error code received from Wedos, code is {response.json()['response']['code']}")

        return response

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


    def add_txt_record(self, domain: str, validation_name: str, validation: str) -> None:
        if any(arg is None for arg in [domain, validation_name, validation]):
            raise errors.Error("Missing important component, this is error from Certbot, not from plugin")

        record = {"domain": domain, 
                  "name": validation_name.replace('.' + domain, ''),
                  "type": "TXT",
                  "ttl": self.ttl,
                  "rdata": validation}

        logger.debug("Creating TXT record ..")
        self._clientConnect("dns-row-add", record)
        logger.debug("TXT Record was created!")
        self._clientConnect("dns-domain-commit", {"name": domain})
        logger.debug("Changes was commit on Wedos")

    def del_txt_record(self, domain: str, validation_name: str, validation: str) -> None:
        if any(arg is None for arg in [domain, validation_name, validation]):
            raise errors.Error("Missing important component, this is error from Certbot, not from plugin")

        logger.debug("Finding ID of TXT record ..")
        response = self._clientConnect("dns-rows-list", {"domain": domain})
        id = self._findID(response.json()["response"],  validation)
        if id == -1:
            logger.warn("Couldn't find created TXT record, is recommended to check it.")
            return

        logger.debug("Deleting created TXT record ..")
        self._clientConnect("dns-row-delete", {"domain": domain, "row_id": id})
        logger.debug("TXT record was deleted!")
        self._clientConnect("dns-domain-commit", {"name": domain})
        logger.debug("Changes was commit on Wedos")



class Authenticator(DNSAuthenticator):
    description = "Obtain certificates for Wedos dns servers."

    def __init__(self, *args: any, **kwargs: any) -> None:
        super(Authenticator, self).__init__(*args, **kwargs)
        self.credentials = None

    def more_info(self) -> str:
        return "This plugin configure a DNS TXT record to respond to a dns-01 challenge using the Hostpoint API"

    def prepare(self) -> None:
        logger.debug("Starting ..")

    def _setup_credentials(self) -> None:
        self.credentials = self._configure_credentials(
            "credentials",
            "Wedos credentials INI file",
            {
                "username": "Username for Wedos API.",
                "password": "Password for Wedos API.",
            },
        )

    def _perform(self, domain: str, validation_name: str, validation: str) -> None:
        self._get_wedos_client().add_txt_record(domain, validation_name, validation)
        logging.debug("Waiting 5 minutes for applied changes on internet")
        time.sleep(300)

    def _cleanup(self, domain: str, validation_name: str, validation: str) -> None:
        self._get_wedos_client().del_txt_record(domain, validation_name, validation)

    def _get_wedos_client(self) -> _WedosClient:
        return _WedosClient(
            self.credentials.conf("username"),  
            self.credentials.conf("password"),
        )