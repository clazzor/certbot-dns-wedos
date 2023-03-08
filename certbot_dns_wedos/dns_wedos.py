#!/usr/bin/python3

import logging, requests, json, hashlib, time
from datetime import datetime
from certbot.plugins.dns_common import DNSAuthenticator
from certbot import errors
logger = logging.getLogger(__name__)


class _WedosClient():
    def __init__(self, username: str, password: str) -> None:
        self.url = "https://api.wedos.com/wapi/json"
        self.username = username
        self.password = password
        self.ttl = 300
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
        return self.session.post(self.url, data={'request': data})

    def _findID(self, data: dict, key: str) -> int:
        ID = None
        for row in data['data']['row']:
            if row['rdata'] == key:
                ID = row['ID']
                break
        return ID

    def add_txt_record(self, domain: str, validation_name: str, validation: str) -> None:
        record = {"domain": domain, 
                  "name": validation_name.replace('.' + domain, ''),
                  "type": "TXT",
                  "ttl": self.ttl,
                  "rdata": validation}

        response = self._clientConnect("dns-row-add", record)
        response = self._clientConnect("dns-domain-commit", {"name": domain})


    def del_txt_record(self, domain: str, validation_name: str, validation: str) -> None:
        response = self._clientConnect("dns-rows-list", {"domain": domain})
        id = self._findID(json.loads(response.text)["response"],  validation)
        response = self._clientConnect("dns-row-delete", {"domain": domain, "row_id": id})
        response = self._clientConnect("dns-domain-commit", {"name": domain})

#class Authenticator(DNSAuthenticator):
class Authenticator():
    description = "Obtain certificates for Wedos dns servers."

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
        self._get_wedos_client().add_txt_record(domain, validation_name, validation)
        time.sleep(300)


    def _cleanup(self, domain: str, validation_name: str, validation: str) -> None:
        self._get_wedos_client().del_txt_record(domain, validation_name, validation)

    def _get_wedos_client(self) -> _WedosClient:
        """return _WedosClient(
            self.credentials.conf("username"),  
            self.credentials.conf("password"),
        )"""
        return _WedosClient(
            "", ""
        )