from setuptools import setup
from setuptools import find_packages

version = "2.0"

install_requires = [
    "certbot>=2.8.0",
    "acme>=2.8.0",
    "setuptools",
    "requests",
    "pytz,"
]

with open("README.md") as f:
    long_description = f.read()

setup(
    name="certbot-dns-wedos",
    version=version,
    description="Wedos DNS Authenticator plugin for Certbot",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/clazzor/certbot-dns-wedos",
    author="Clazzor",
    license="Apache License 2.0",
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Plugins",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Security",
        "Topic :: System :: Installation/Setup",
        "Topic :: System :: Networking",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
    ],
    packages=find_packages(),
    include_package_data=True,
    install_requires=install_requires,
    entry_points={
        "certbot.plugins": [
            "dns-wedos = certbot_dns_wedos.dns_wedos:Authenticator"
        ]
    },
)