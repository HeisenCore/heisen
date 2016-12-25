#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

# install_reqs = parse_requirements('requirements.txt', session=False)

core_requirements = [           # heisen can't start without these
    'Twisted',
    'txJSON_RPC_heisen==0.4.5',
    'jsonrpclib_heisen<=0.1.14',
    'cliff==2.1.0',
    'zope.interface==4.0.5',
]

optional_requirements = [       # heisen must function without these
    'pymongo==3.0.3',
    'pytz==2016.6.1',
    'import_string==0.1.0',
    'Cerberus==1.0.1',
    'apscheduler==3.2.0',
    'Jinja2==2.8',
    'watchdog==0.8.3',
    'docutils==0.12',
    'elasticsearch==5.0.1',
    # 'cython==0.24.1',
]

requirements = core_requirements + optional_requirements

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='heisen',
    version='0.1.0',
    description="Awesome heisen",
    long_description=readme + '\n\n' + history,
    author="Keyvan Hedayati",
    author_email='k1.hedayati93@gmail.com',
    url='https://github.com/HeisenCore/heisen',
    packages=find_packages(),
    package_dir={'heisen': 'heisen'},
    entry_points={
        'console_scripts': [
            'heisen=heisen.cli:main'
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    dependency_links=[
        'https://github.com/HeisenCore/txjsonrpc/tarball/master#egg=txJSON_RPC_heisen-0.4.5',
        'https://github.com/HeisenCore/jsonrpclib/tarball/master#egg=jsonrpclib_heisen-0.1.14',
    ],
    license="MIT license",
    zip_safe=False,
    keywords='heisen',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
