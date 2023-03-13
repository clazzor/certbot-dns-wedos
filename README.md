# CertBot DNS plugin
This plugin uses [certbot](https://github.com/certbot/certbot)'s [dns-01 challenge](https://letsencrypt.org/docs/challenge-types/) to create and delete TXT records on a [Wedos](https://www.wedos.com/) domain server, thanks to the API interface called [WAPI](https://kb.wedos.com/en/kategorie/wapi-api-interface/) provided by [Wedos](https://www.wedos.com/).

## Installation
### Prerequirements
For the functionality of this plugin, you will need to install these programs/softwares.
| Name                                           | Install                                                                       | Version   |
|:----------------------------------------------:|:-----------------------------------------------------------------------------:|:----------|
| [python](https://github.com/python/cpython)    | [Link](https://packaging.python.org/en/latest/tutorials/installing-packages/) | >= 3.7    |
| [pip](https://github.com/pypa/pip/)            | [Link](https://pip.pypa.io/en/stable/installation/)                           | >= 18.1   |
| [certbot](https://github.com/certbot/certbot/) | [Link](https://certbot.eff.org/instructions/)                                 | >= 0.34.0 |

> _Note that in theory, even the oldest versions that are mentions should work, but the test was conducted on a Debian 10 system with Python 3.9.2, pip3 20.3.4, and Certbot 2.2.0, so there may be compatibility issues._

You will also **need to have WAPI activated** for communication between Wedos and the plugin. To activate WAPI, you can read the article from Wedos, available at this [link](https://kb.wedos.com/en/wapi-api-interface/wapi-activation-and-settings/).
> **CAUTION: Please note that the IP address of the server where Certbot with the plugin will be located must be allowed, otherwise it will not work.**

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
### credentials
### Configuration file INI
### Arguments
### Example

## Used Modules/Libraries
I just want to mention which modules/libraries this plugin uses for better debugging of errors in the future, in case any occur.

| Name                                                                     | License                                                          |
|:------------------------------------------------------------------------:|:----------------------------------------------------------------:|
| [setuptools](https://github.com/pypa/setuptools)                         | [MIT](https://github.com/pypa/setuptools/blob/main/LICENSE/)     |
| [requests](https://github.com/psf/requests)                              | [Apache 2.0](https://github.com/psf/requests/blob/main/LICENSE/) |
| [logging](https://github.com/python/cpython/tree/main/Lib/logging)       | [PSF](https://github.com/python/cpython/blob/main/LICENSE/)      |
| [json](https://github.com/python/cpython/tree/3.11/Lib/json)             | [PSF](https://github.com/python/cpython/blob/main/LICENSE/)      |
| [haslib](https://github.com/python/cpython/blob/3.11/Lib/hashlib.py)     | [PSF](https://github.com/python/cpython/blob/main/LICENSE/)      |
| [time](https://github.com/python/cpython/blob/main/Modules/timemodule.c) | [PSF](https://github.com/python/cpython/blob/main/LICENSE/)      |
| [datetime](https://github.com/python/cpython/blob/3.11/Lib/datetime.py)  | [PSF](https://github.com/python/cpython/blob/main/LICENSE/)      |

## Errors
If an error occurs, Certbot will display the type of error that has occurred.  
If it is an error related to communication between the plugin and WAPI, you will receive a [return code](https://en.wikipedia.org/wiki/Exit_status). Wedos has a list of error codes on their Czech website, which you can access through this [link](https://kb.wedos.com/cs/wapi-api-rozhrani/zakladni-informace-wapi-api-rozhrani/wapi-seznam-navratovych-kodu/). _(If you do not speak Czech, you can use [Google Translate](https://kb-wedos-com.translate.goog/cs/wapi-api-rozhrani/zakladni-informace-wapi-api-rozhrani/wapi-seznam-navratovych-kodu/?_x_tr_sl=en&_x_tr_tl=cs&_x_tr_hl=cs&_x_tr_pto=wapp) :D)_

