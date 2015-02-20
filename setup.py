from __future__ import unicode_literals

import os
import re
import setuptools


version = (
    re
    .compile(r".*__version__ = '(.*?)'", re.S)
    .match(open('frl/__init__.py').read())
    .group(1)
)

packages = [
    str(s) for s in
    setuptools.find_packages('.', exclude=('tests', 'tests.*'))
]

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.md')) as f:
    README = f.read()

with open(os.path.join(here, 'CHANGES.txt')) as f:
    CHANGES = f.read()

requires = []

extras_require = {
    'tests': [
        'nose',
        'pytest',
        'pyflakes',
        'webtest',
        'WSGIProxy2',
        'mock',
        'ipdb'
    ],
    'client': [
        'requests',
    ],
    'server': [
        'Flask',
    ]
}

scripts = [
]


setuptools.setup(
    name='frl',
    version=version,
    description='flask/requests logging',
    long_description=README + '\n\n' + CHANGES,
    classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: MIT License",
    ],
    author='Balanced',
    author_email='dev+frl@balancedpayments.com',
    license='The MIT License: http://www.opensource.org/licenses/mit-license.php',
    packages=packages,
    include_package_data=True,
    zip_safe=False,
    scripts=scripts,
    install_requires=requires,
    extras_require=extras_require,
    tests_require=extras_require['tests'],
    test_suite='nose.collector',
)
