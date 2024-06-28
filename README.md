# CertBot DNS plugin
This plugin uses [certbot](https://github.com/certbot/certbot)'s [dns-01 challenge](https://letsencrypt.org/docs/challenge-types) to create and delete TXT records on a [Wedos](https://www.wedos.com) domain server, thanks to the API interface called [WAPI](https://kb.wedos.com/en/kategorie/wapi-api-interface) provided by [Wedos](https://www.wedos.com). With this plugin you can make [wildcard](https://en.wikipedia.org/wiki/Wildcard_DNS_record) [ssl](https://letsencrypt.org/docs/faq/#does-let-s-encrypt-issue-wildcard-certificates). 

## Installation
### Prerequirements
For the functionality of this plugin, you will need to install these programs/softwares.
| Name                                           | Install                                                                      | Version   |
|:----------------------------------------------:|:----------------------------------------------------------------------------:|:---------:|
| [python](https://github.com/python/cpython)    | [Link](https://packaging.python.org/en/latest/tutorials/installing-packages) | >= 3.8.0  |
| [pip](https://github.com/pypa/pip/)            | [Link](https://pip.pypa.io/en/stable/installation)                           | >= 19.2.3 |
| [certbot](https://github.com/certbot/certbot/) | [Link](https://certbot.eff.org/instructions)                                 | >= 2.8.0  |
> _Note that in theory, even an older version should work, but it has not been tested._

### WAPI
You will also **need to have WAPI activated** for communication between Wedos and the plugin. To activate WAPI, you can read the article from Wedos, available at this link [WAPI activation and settings](https://kb.wedos.com/en/wapi-api-interface/wapi-activation-and-settings).
> **CAUTION: Please note that the IP address of the server where Certbot with the plugin will be located must be allowed on WAPI, otherwise it will not work.**

### The Install
#### With pip (recommend)
```commandline
pip install certbot-dns-wedos --break-system-packages
```
---

#### From source
```commandline
git clone https://github.com/clazzor/certbot-dns-wedos.git
pip install ./certbot-dns-wedos --break-system-packages
```
After installation, the created folders may be deleted.
```commandline
rm -r certbot-dns-wedos
```

## Setup
### Arguments 
| Name                            | Required           | Description                                                                          |
|:--------------------------------|:------------------:|:-------------------------------------------------------------------------------------|
| --dns-wedos-propagation-seconds | :x:                | Seconds to wait for DNS propagation before verifying DNS record with ACME server.    |
| --dns-wedos-credentials         | :white_check_mark: | The complete path to the INI file for credentials containing data for authorization. |
> The default value of `propagation-seconds` is 420, if there is a problem with validation, increase the number. The lower limit is 300.

### Command example
The basic structure of the command is the same as with all other cerbot plugins, we define which plugin to use, propagation-seconds, credentials file and domains, like this:
```commandline
certbot certonly \
--authenticator dns-wedos \
--dns-wedos-propagation-seconds 420 \
--dns-wedos-credentials /path/to/the/file.ini \
-d example.com -d *.example.com
```

### Credentials file
| Name           | Required           | Description                   |
|:---------------|:------------------:|:------------------------------|
| dns_wedos_user | :white_check_mark: | The user (email) for WAPI.    |
| dns_wedos_auth | :white_check_mark: | The auth (password) for WAPI. |

This is what the credentials file for wedos plugin should look like.
```commandline
dns_wedos_user=user@example.com
dns_wedos_auth=examplepassword
```
* Values are written after an equal&#160;sign&#160;`=`. For values with spaces, such as `hello world`, a space can be used.
* **For the ini file you should apply permission: `chmod 600 file.ini` for security reason.**

## Reloading certificates on services
Usually services like haproxy, nginx, apache and more need to restart to retrieve a new certificate. 
For this is used the `deploy hook`.<br>
More information on this repository: [Load a new certificate after a successful renewal](https://github.com/clazzor/deploy-service-restart)

## Errors
If an error occurs, Certbot will display the type of error that has occurred.  
* If you get this error "*Certbot failed to authenticate some domains (authenticator: dns-wedos)*", increase the number in the `--dns-wedos-propagation-seconds` argument.
* If you encounter an [HTTP error](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status) related to communication with WAPI, you will receive an [HTTP error](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status).
* If it is an error related to communication between the plugin and WAPI, you will receive a [return code](https://en.wikipedia.org/wiki/Exit_status). Wedos has a list of error codes on their website, which you can access through this link [WAPI list of return codes](https://kb.wedos.com/en/wapi-api-interface/wapi-manual/#return-codes).

## Used Modules/Libraries
I just want to mention which modules/libraries this plugin uses for better debugging of errors in the future, in case any occur.
| Name                                                                    | License                                                                  |
|:-----------------------------------------------------------------------:|:------------------------------------------------------------------------:|
| [certbot](https://github.com/certbot/certbot)                           | [Apache 2.0](https://github.com/certbot/certbot/blob/master/LICENSE.txt) |
| [datetime](https://github.com/python/cpython/blob/main/Lib/datetime.py) | [PSF](https://github.com/python/cpython/blob/main/LICENSE)               |
| [hashlib](https://github.com/python/cpython/blob/main/Lib/hashlib.py)   | [PSF](https://github.com/python/cpython/blob/main/LICENSE)               |
| [json](https://github.com/python/cpython/blob/main/Lib/json)            | [PSF](https://github.com/python/cpython/blob/main/LICENSE)               |
| [logging](https://github.com/python/cpython/blob/main/Lib/logging)      | [PSF](https://github.com/python/cpython/blob/main/LICENSE)               |
| [pytz](https://github.com/stub42/pytz)                                  | [MIT](https://github.com/stub42/pytz/blob/master/LICENSE.txt)            |
| [re](https://github.com/python/cpython/blob/main/Lib/re)                | [PSF](https://github.com/python/cpython/blob/main/LICENSE)               |
| [requests](https://github.com/psf/requests)                             | [Apache 2.0](https://github.com/psf/requests/blob/main/LICENSE)          |
| [setuptools](https://github.com/pypa/setuptools)                        | [MIT](https://github.com/pypa/setuptools/blob/main/LICENSE)              |
| [typing](https://github.com/python/cpython/blob/main/Lib/typing.py)     | [PSF](https://github.com/python/cpython/blob/main/LICENSE)               |
