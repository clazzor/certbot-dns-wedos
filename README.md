# CertBot DNS plugin
This plugin uses [certbot](https://github.com/certbot/certbot)'s [dns-01 challenge](https://letsencrypt.org/docs/challenge-types) to create and delete TXT records on a [Wedos](https://www.wedos.com) domain server, thanks to the API interface called [WAPI](https://kb.wedos.com/en/kategorie/wapi-api-interface) provided by [Wedos](https://www.wedos.com). With this plugin you can make [wildcard](https://en.wikipedia.org/wiki/Wildcard_DNS_record) [ssl](https://letsencrypt.org/docs/faq/#does-let-s-encrypt-issue-wildcard-certificates). 

## Installation
### Prerequirements
For the functionality of this plugin, you will need to install these programs/softwares.
| Name                                           | Install                                                                       | Version   |
|:----------------------------------------------:|:-----------------------------------------------------------------------------:|:----------|
| [python](https://github.com/python/cpython)    | [Link](https://packaging.python.org/en/latest/tutorials/installing-packages) | >= 3.7    |
| [pip](https://github.com/pypa/pip/)            | [Link](https://pip.pypa.io/en/stable/installation)                           | >= 18.1   |
| [certbot](https://github.com/certbot/certbot/) | [Link](https://certbot.eff.org/instructions)                                 | >= 0.34.0 |

> _Note that in theory, even the oldest versions that are mentions should work, but the test was conducted on a Debian 10 system with Python 3.9.2, pip3 20.3.4, and Certbot 2.2.0, so there may be compatibility issues._

You will also **need to have WAPI activated** for communication between Wedos and the plugin. To activate WAPI, you can read the article from Wedos, available at this link [WAPI activation and settings](https://kb.wedos.com/en/wapi-api-interface/wapi-activation-and-settings).
> **CAUTION: Please note that the IP address of the server where Certbot with the plugin will be located must be allowed on WAPI, otherwise it will not work.**

### The Install
First, we will download the source code from GitHub, and then we can install the plugin using pip.

With `git`
```commandline
git clone https://github.com/clazzor/certbot-dns-wedos.git
cd certbot-dns-wedos
pip3 install .
```

With `wget`   
```commandline
wget https://github.com/clazzor/certbot-dns-wedos/archive/refs/heads/main.zip -O wedos.zip
unzip wedos.zip -d wedos
cd wedos/certbot-dns-wedos
pip3 install .
```

With `curl`
```commandline
curl -L https://github.com/clazzor/certbot-dns-wedos/archive/refs/heads/main.zip --output wedos.zip
unzip wedos.zip -d wedos
cd wedos/certbot-dns-wedos
pip3 install .
```
---
After installation, the created folders may be deleted.

If you have used it `git`
```commandline
cd .. 
rm -r certbot-dns-wedos
```

If you have used it `wget` or `curl`
```commandline
cd .. 
rm -r wedos.zip wedos
```

## Setup
### Certbot Command
The basic structure of the command is the same as with all other plugins, we define the plugin and domains, like this:
```commandline
certbot certonly \
--authenticator dns-wedos \
-d *.example.com \
-d example.com
```
In any case, without entering the required command/plugin parameters, it cannot function!

---

### Arguments and credentials
To ensure proper functionality of the plugin, it is necessary to set some parameters. Here are the arguments/credentials:

| Name                       | Argument                   | Credential       | Description                                                                       |
|:---------------------------|:--------------------------:|:----------------:|:---------------------------------------------------------------------------------:|
| propagation&#x2011;seconds | Optional (default&#160;30) | Not&#160;allowed | Seconds to wait for DNS propagation before verifying DNS record with ACME server. |
| credentials                | Optional                   | Not&#160;allowed | The complete path to the INI file for credentials.                                |
| user                       | Required&#160;*            | Required         | The user (username) for WAPI.                                                     |
| auth                       | Required&#160;*            | Required         | The auth (password) for WAPI and must be encrypted using SHA1.                    |
| finalize                   | Optional                   | Optinal          | The command to be executed at the end.                                            |

> \* Only required if the path to the credentials is not defined!

* **CAUTION: The auth (password) must be entered as an encrypted password using SHA1. You can use a website like this one to encrypt your password [emn178 sha1](https://emn178.github.io/online-tools/sha1.html)!**
* **If the credential path is defined, then the user and auth must be defined in INI file as well. Otherwise, an error will occur.**
* **The arguments overwrite the credentials data.**

### Parametr Structure
For `arguments`  
* The prefix --dns-wedos is used for arguments, and values are written after a space. For values with spaces, such as `hello world`, quotes&#160;`"` or apostrophes&#160;`'` are used.
```commandline
--dns-wedos-<NameOfArgument> <Value>
```
Example:
```commandline
--dns-wedos-finalize "nginx -s reload"
```

For `credential`  
* The prefix dns_wedos_ is used for credentials, and values are written after an equal&#160;sign&#160;`=`. For values with spaces, such as `hello world`, a space can be used.
* For the ini file you must apply permission: `chmod 600 file.ini`
```commandline
dns_wedos_<NameOfArgument>=<Value>
```
Example:
```commandline
dns_wedos_finalize=nginx -s reload
```

---

### Examples
Using `credential`
```commandline
certbot certonly --authenticator dns-wedos \
--dns-wedos-credentials /path/to/the/file.ini \
-d *.example.com -d example.com
```

The `/path/to/the/file.ini` file:
```commandline
dns_wedos_user=user@example.com
dns_wedos_auth=c3499c2729730a7f807efb8676a92dcb6f8a3f8f
```
---

Using `arguments`
```commandline
certbot certonly --authenticator dns-wedos \
--dns-wedos-user=user@example.com \
--dns-wedos-auth=c3499c2729730a7f807efb8676a92dcb6f8a3f8f \
-d *.example.com -d example.com
```

---

Using `credentials` and `arguments`  
_(arguments overwrite the credentials so user will be `admin@example.com`)_
```commandline
certbot certonly --authenticator dns-wedos \
--dns-wedos-user admin@example.com \
--dns-wedos-finalize "nginx -s reload" \
--dns-wedos-credentials /path/to/the/file.ini \
-d *.example.com -d example.com
```

The `/path/to/the/file.ini` file:
```commandline
dns_wedos_user=user@example.com
dns_wedos_auth=c3499c2729730a7f807efb8676a92dcb6f8a3f8f
```
> _Note: `c3499c2729730a7f807efb8676a92dcb6f8a3f8f` is encrypted word `test` with sha1_

## Used Modules/Libraries
I just want to mention which modules/libraries this plugin uses for better debugging of errors in the future, in case any occur.

| Name                                                                        | License                                                         |
|:---------------------------------------------------------------------------:|:---------------------------------------------------------------:|
| [setuptools](https://github.com/pypa/setuptools)                            | [MIT](https://github.com/pypa/setuptools/blob/main/LICENSE)     |
| [requests](https://github.com/psf/requests)                                 | [Apache 2.0](https://github.com/psf/requests/blob/main/LICENSE) |
| [subprocess](https://github.com/python/cpython/blob/3.11/Lib/subprocess.py) | [PSF](https://github.com/python/cpython/blob/main/LICENSE)      |
| [logging](https://github.com/python/cpython/tree/main/Lib/logging)          | [PSF](https://github.com/python/cpython/blob/main/LICENSE)      |
| [haslib](https://github.com/python/cpython/blob/3.11/Lib/hashlib.py)        | [PSF](https://github.com/python/cpython/blob/main/LICENSE)      |
| [shelx](https://github.com/python/cpython/blob/3.11/Lib/shlex.py)           | [PSF](https://github.com/python/cpython/blob/main/LICENSE)      |
| [json](https://github.com/python/cpython/tree/3.11/Lib/json)                | [PSF](https://github.com/python/cpython/blob/main/LICENSE)      |
| [time](https://github.com/python/cpython/blob/main/Modules/timemodule.c)    | [PSF](https://github.com/python/cpython/blob/main/LICENSE)      |

## Errors
If an error occurs, Certbot will display the type of error that has occurred.  
* If you encounter an [HTTP error](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status) related to communication with WAPI, you will receive an [HTTP error](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status).
* If it is an error related to communication between the plugin and WAPI, you will receive a [return code](https://en.wikipedia.org/wiki/Exit_status). Wedos has a list of error codes on their Czech website, which you can access through this link [WAPI list of return codes](https://kb.wedos.com/cs/wapi-api-rozhrani/zakladni-informace-wapi-api-rozhrani/wapi-seznam-navratovych-kodu). _(If you do not speak Czech, you can use [Google Translate](https://kb-wedos-com.translate.goog/cs/wapi-api-rozhrani/zakladni-informace-wapi-api-rozhrani/wapi-seznam-navratovych-kodu/?_x_tr_sl=cs&_x_tr_tl=en) :D)_
* If there is an error with the command you entered as the `finalize` parameter, you will receive a [error code](https://en.wikipedia.org/wiki/Error_code) and error text similar to what you would get if you entered it in the terminal.