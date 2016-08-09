#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

install_reqs = parse_requirements('requirements.txt', session=False)

requirements = [str(ir.req) for ir in install_reqs]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='core',
    version='0.1.0',
    description="Awesome Core",
    long_description=readme + '\n\n' + history,
    author="Keyvan Hedayati",
    author_email='k1.hedayati93@gmail.com',
    url='https://github.com/k1-hedayati/core',
    packages=[
        'core',
    ],
    package_dir={'core':
                 'core'},
    entry_points={
        'console_scripts': [
            'core=core.cli:main'
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='core',
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
