#!/usr/bin/env python

import os
import re

from setuptools import setup

CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))

def get_reqs(*fns):
    lst = []
    for fn in fns:
        for package in open(os.path.join(CURRENT_DIR, fn)).readlines():
            package = package.strip()
            if not package:
                continue
            lst.append(package.strip())
    return lst

with open("godaddypy/__init__.py", "r") as f:
    version_match = re.search(r"^__version__\s*=\s*[\'\"]([^\'\"]*)[\'\"]", f.read(), re.MULTILINE)

if version_match is None:
    raise RuntimeError("No version information found in godaddypy/__init__.py")
else:
    version = version_match.group(1)

with open("README.rst") as file:
    long_description = file.read()

setup(
    name="GoDaddyPy",
    version=version,
    description="A very simple python client used to update the IP address in A records for GoDaddy managed domains.",
    long_description=long_description,
    author="Julian Coy",
    author_email="julian.calvin.coy@gmail.com",
    url="https://github.com/eXamadeus/godaddypy",
    packages=["godaddypy"],
    install_requires=get_reqs('requirements.txt'),
    tests_require=get_reqs('requirements-dev.txt'),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Topic :: Internet :: Name Service (DNS)",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    project_urls={
        "Source": "https://github.com/eXamadeus/godaddypy",
    },
)
