from requests import Session, post
from subprocess import run, PIPE
from logging import getLogger
from hashlib import sha1
from shlex import split
from json import dumps
from time import strftime, localtime, sleep
from certbot.plugins.dns_common import DNSAuthenticator, validate_file_permissions
from certbot import errors

logger = getLogger(__name__)
URL = "https://api.wedos.com/wapi/json"
TTL = 300

class _WedosClient():

    def __init__(self, username: str, password: str) -> None:
        self.url = URL
        self.username = username
        self.password = password
        self.ttl = TTL
        self.session = Session()


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

    def _clientConnect(self, command: str, params: dict = None, debug: str = "") -> post:
        logger.debug(debug)
        auth = (self.username + self.password + strftime('%H', localtime())).encode("ascii")

        data = {
            "user": self.username,
            "auth": sha1(auth).hexdigest(),
            "command": command
            }

        if type(params) is dict: data.update({"data": params})
        data = dumps({"request": data})
        response = self.session.post(self.url, data={'request': data})

        if not response.ok:
            raise errors.PluginError(f"Cannot access Api Wedos, HTTP error code is {response.status_code}")

        if response.json()["response"]["code"] >= 2000:
            raise errors.PluginError(f"Error code received from Wedos, code is {response.json()['response']['code']}")

        return response


    def add_txt_record(self, domain: str, validation_name: str, validation: str) -> None:
        if any(arg is None for arg in [domain, validation_name, validation]):
            raise errors.Error("Missing important component, this is error from Certbot, not from plugin")

        record = {"domain": domain,
                  "name": validation_name.replace('.' + domain, ''),
                  "type": "TXT",
                  "ttl": self.ttl,
                  "rdata": validation}

        self._clientConnect("dns-row-add", record, "Creating TXT record ..")
        self._clientConnect("dns-domain-commit", {"name": domain}, "TXT Record was created!")
        logger.debug("Changes was commit on Wedos")

    def del_txt_record(self, domain: str, validation_name: str, validation: str) -> None:
        if any(arg is None for arg in [domain, validation_name, validation]):
            raise errors.Error("Missing important component, this is error from Certbot, not from plugin")

        response = self._clientConnect("dns-rows-list", {"domain": domain}, "Finding ID of TXT record ..")
        id = self._findID(response.json()["response"],  validation)
        if id == -1:
            logger.warn("Couldn't find created TXT record, is recommended to check it.")
            return

        self._clientConnect("dns-row-delete", {"domain": domain, "row_id": id}, "Deleting created TXT record ..")
        self._clientConnect("dns-domain-commit", {"name": domain}, "TXT record was deleted!")
        logger.debug("Changes was commit on Wedos")


class Authenticator(DNSAuthenticator):

    description = "Obtain certificates for Wedos dns servers."

    def __init__(self, *args: any, **kwargs: any) -> None:
        super(Authenticator, self).__init__(*args, **kwargs)
        self.credentials = None
        self.arguments = {}

        for arg in ["credentials", "user", "auth", "finalize"]:
            if self.conf(arg): self.arguments[arg] = self.conf(arg)
            else: self.arguments[arg] = None


    @classmethod
    def add_parser_arguments(cls, add: callable) -> None:
        super(Authenticator, cls).add_parser_arguments(add, default_propagation_seconds=30)
        add("credentials", help="Wedos credentials INI file.")
        add("user", help="User for Wedos API. (Overwrite INI file)")
        add("auth", help="SHA1 Auth (Password) for Wedos API. (Overwrite INI file)")
        add("finalize", help="Path or command that will run after everything is done. (Overwrite INI file)")


    def more_info(self) -> str:
        return "This plugin uses certbot's dns-01 challenge to create and delete TXT records\
                on a Wedos domain server, thanks to the API interface called WAPI provided by Wedos.\
                With this plugin, you can make wildcard ssl."

    def _get_credentials(self) -> None:
        self._configure_file('credentials', "Wedos credentials INI file.")
        validate_file_permissions(self.arguments["credentials"])

        self.credentials = self._configure_credentials(
            "credentials",
            "Wedos credentials INI file.",
            {
                "user": "User for Wedos API.",
                "auth": "SHA1 Auth (Password) for Wedos API.",
            },
        )

    def _setup_credentials(self) -> None:
        if self.arguments["credentials"]: self._get_credentials()

        for arg in ["user", "auth", "finalize"]:
            if not self.credentials or not self.credentials.conf(arg): continue
            self.arguments[arg] = self.arguments[arg] or self.credentials.conf(arg)

        if not self.arguments["user"]:
            raise errors.PluginError("Missing or incorrect argument 'user' for WAPI.")
        if not self.arguments["auth"]:
            raise errors.PluginError("Missing or incorrect argument 'auth' for WAPI.")


    def _perform(self, domain: str, validation_name: str, validation: str) -> None:
        logger.debug("Starting ..")
        domain = '.'.join(domain.split('.')[-2:])
        self._get_wedos_client().add_txt_record(domain, validation_name, validation)
        logger.debug("Waiting 5 minutes for applied changes on internet")
        sleep(300)

    def _cleanup(self, domain: str, validation_name: str, validation: str) -> None:
        domain = '.'.join(domain.split('.')[-2:])
        self._get_wedos_client().del_txt_record(domain, validation_name, validation)

        logger.debug(f"Processing final command: {self.arguments['finalize']}")
        if not self.arguments["finalize"]: return
        process = run(split(self.arguments["finalize"]), shell=False, stderr=PIPE)

        if process.returncode != 0:
            logger.warn(f"Command: \"{self.arguments['finalize']}\" returned non-zero exit status\
                        {process.returncode} with error message:\n{process.stderr.decode().strip()}")

    def _get_wedos_client(self) -> _WedosClient:
        return _WedosClient(self.arguments["user"], self.arguments["auth"])
