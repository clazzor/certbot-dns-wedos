# CertBot DNS plugin
This plugin uses [certbot](https://github.com/certbot/certbot)'s [dns-01 challenge](https://letsencrypt.org/docs/challenge-types) to create and delete TXT records on a [Wedos](https://www.wedos.com) domain server, thanks to the API interface called [WAPI](https://kb.wedos.global/wapi/) provided by [Wedos](https://www.wedos.com). With this plugin you can issue [wildcard](https://en.wikipedia.org/wiki/Wildcard_DNS_record) [SSL/TLS](https://letsencrypt.org/docs/faq/#does-let-s-encrypt-issue-wildcard-certificates) certificates. 

## Installation
### Prerequisites
The following software is required to use this plugin.
| Name                                           | Install                                                                      | Version   |
|:----------------------------------------------:|:----------------------------------------------------------------------------:|:---------:|
| [python](https://github.com/python/cpython)    | [Link](https://www.python.org/downloads/)                                    | >= 3.10.0 |
| [pip](https://github.com/pypa/pip/)            | [Link](https://pip.pypa.io/en/stable/installation)                           | >= 24.1   |
| [certbot](https://github.com/certbot/certbot/) | [Link](https://certbot.eff.org/instructions)                                 | >= 3.0.0  |
> _Note that in theory, even older versions should work, but it has not been tested._

### WAPI
You will also **need to have WAPI activated** for communication between Wedos and the plugin. To activate WAPI, you can read the article from Wedos, available at this link [WAPI activation and settings](https://kb.wedos.global/wapi-manual/#activate).
> **CAUTION: Please note that the IP address of the server where Certbot with the plugin will be located must be whitelisted in WAPI, otherwise it will not work.**

### Installation methods
#### With snap (recommended)
```commandline
snap install certbot-dns-wedos
sudo snap set certbot trust-plugin-with-root=ok
sudo snap connect certbot:plugin certbot-dns-wedos
```
---
#### With pip
```commandline
sudo pip install certbot-dns-wedos
```
---
#### From source
```commandline
git clone https://github.com/clazzor/certbot-dns-wedos.git
sudo pip install ./certbot-dns-wedos
```
After installation, the cloned repository can be deleted.
```commandline
rm -r certbot-dns-wedos
```

## Setup
### Arguments 
| Name                            | Required | Description                                                                          |
|:--------------------------------|:--------:|:-------------------------------------------------------------------------------------|
| --dns-wedos-propagation-seconds | ❌       | Seconds to wait for DNS propagation before verifying the DNS record with ACME server.    |
| --dns-wedos-credentials         | ✅       | The complete path to the INI file for credentials containing data for authorization. |
> The default value of `propagation-seconds` is 450. If there is a problem with validation, increase the number. The lower limit is 300.

### Command example
The basic structure of the command is the same as with all other certbot plugins, we define which plugin to use, propagation-seconds, credentials file and domains, like this:
```commandline
certbot certonly \
--authenticator dns-wedos \
--dns-wedos-propagation-seconds 450 \
--dns-wedos-credentials /path/to/the/file.ini \
-d example.com -d *.example.com
```

### Credentials file
| Name           | Required | Description                                   |
|:---------------|:--------:|:----------------------------------------------|
| dns_wedos_user | ✅       | The user (email) for WAPI.                   |
| dns_wedos_auth | ✅       | The auth (password) for WAPI.                |
| dns_wedos_ttl  | ❌       | The TTL for the DNS record. (default: 300)   |

This is what the credentials file for the wedos plugin should look like.
```commandline
dns_wedos_user=user@example.com
dns_wedos_auth=examplepassword
```
* Values are written after an equals&#160;sign&#160;`=`. For values with spaces, such as `hello world`, a space can be used.
* **For the ini file you should apply permission: `chmod 600 file.ini` for security reasons.**

## Reloading certificates on services
Usually services like haproxy, nginx, apache and more need to reload to retrieve a new certificate. 
The `--deploy-hook` is used for this purpose.

### Example
```commandline
certbot certonly \
--authenticator dns-wedos \
--dns-wedos-propagation-seconds 450 \
--dns-wedos-credentials /path/to/the/file.ini \
-d example.com -d *.example.com \
--deploy-hook "COMMAND_TO_RELOAD_SERVICE"
```

### Nginx
```commandline
--deploy-hook "systemctl reload nginx"
```

### Apache
```commandline
--deploy-hook "systemctl reload apache2"
```

### HAProxy
HAProxy requires the certificate and private key to be joined into a single `.pem` file:
```commandline
--deploy-hook "cat /etc/letsencrypt/live/example.com/fullchain.pem /etc/letsencrypt/live/example.com/privkey.pem > /etc/haproxy/certs/combined.pem && systemctl reload haproxy"
```

## Errors
If an error occurs, Certbot will display the type of error that has occurred.  
* If you get this error "*Certbot failed to authenticate some domains (authenticator: dns-wedos)*", increase the value in the `--dns-wedos-propagation-seconds` argument.
* Standard [HTTP error](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status) codes are returned in case of communication issues with the WAPI endpoint.
* If it is an error related to communication between the plugin and WAPI, you will receive a [WAPI return code](https://kb.wedos.global/wapi-codes/).

## Used Modules/Libraries
The following modules and libraries are used by this plugin (useful for debugging purposes):
| Name                                                                    | License                                                                          |
|:-----------------------------------------------------------------------:|:--------------------------------------------------------------------------------:|
| [certbot](https://github.com/certbot/certbot)                           | [Apache 2.0](https://github.com/certbot/certbot/blob/master/LICENSE.txt)         |
| [datetime](https://github.com/python/cpython/blob/main/Lib/datetime.py) | [PSF](https://github.com/python/cpython/blob/main/LICENSE)                       |
| [hashlib](https://github.com/python/cpython/blob/main/Lib/hashlib.py)   | [PSF](https://github.com/python/cpython/blob/main/LICENSE)                       |
| [json](https://github.com/python/cpython/blob/main/Lib/json)            | [PSF](https://github.com/python/cpython/blob/main/LICENSE)                       |
| [logging](https://github.com/python/cpython/blob/main/Lib/logging)      | [PSF](https://github.com/python/cpython/blob/main/LICENSE)                       |
| [typing](https://github.com/python/cpython/blob/main/Lib/typing.py)     | [PSF](https://github.com/python/cpython/blob/main/LICENSE)                       |
| [pytz](https://github.com/stub42/pytz)                                  | [MIT](https://github.com/stub42/pytz/blob/master/LICENSE.txt)                    |
| [requests](https://github.com/psf/requests)                             | [Apache 2.0](https://github.com/psf/requests/blob/main/LICENSE)                  |
| [setuptools](https://github.com/pypa/setuptools)                        | [MIT](https://github.com/pypa/setuptools/blob/main/LICENSE)                      |
| [tldextract](https://github.com/john-kurkowski/tldextract)              | [BSD 3-Clause](https://github.com/john-kurkowski/tldextract/blob/master/LICENSE) |
