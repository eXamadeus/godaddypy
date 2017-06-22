#!/usr/bin/env python

import re

from setuptools import setup

with open('godaddypy/__init__.py', 'r') as f:
    version_match = re.search(r'^__version__\s*=\s*[\']([^\']*)[\']',
                              f.read(), re.MULTILINE)

if version_match is None:
    raise RuntimeError('No version information found in godaddypy/__init__.py')
else:
    version = version_match.group(1)

setup(name='GoDaddyPy',
      version=version,
      description='A very simple python client used to update the IP address in A records for GoDaddy managed domains.',
      author='Julian Coy',
      author_email='julian.calvin.coy@gmail.com',
      url='https://github.com/eXamadeus/godaddypy',
      packages=['godaddypy'],
      install_requires=[
          'requests>=2.4'
      ],
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: Developers',
          'Intended Audience :: System Administrators',
          'Topic :: Internet :: Name Service (DNS)',
          'License :: OSI Approved :: BSD License',
          'Natural Language :: English',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.2',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5'
      ])
