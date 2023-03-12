from setuptools import setup
from setuptools import find_packages

version = "0.8"

install_requires = [
    "acme>=0.29.0",
    "certbot>=0.34.0",
    "setuptools",
    "requests",
]

with open("README.md") as f:
    long_description = f.read()

setup(
    name="certbot-dns-wedos",
    version=version,
    description="Wedos DNS Authenticator plugin for Certbot",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/clazzor/certbot-dns-wedos",
    author="Clazzor",
    license="Apache License 2.0",
    python_requires=">=3.0",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Plugins',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Security',
        'Topic :: System :: Installation/Setup',
        'Topic :: System :: Networking',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities',
    ],
    packages=find_packages(),
    include_package_data=True,
    install_requires=install_requires,
    entry_points={
        "certbot.plugins": [
            "dns-wedos = certbot_dns_wedos.dns_wedos:Authenticator"
        ]
    },
     test_suite="certbot_dns_wedos",
)