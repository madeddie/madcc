from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='madcc',
    version='0.0.2-alpha.2',
    description='madtech cryptocurrency functions',
    long_description=long_description,
    url='https://github.com/madeddie/madcc',
    author='Edwin Hermans',
    author_email='edwin@madtech.cx',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],

    keywords='personal project cryptocurrency kraken gdax coinmarketcap',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),

    install_requires=[
        'clint',
        'coinmarketcap',
        'krakenex',
        'requests',
        'tabulate',
    ],
    python_requires='~=3.4',

    entry_points={
        'console_scripts': [
            'kraken_limits=madcc.entrypoints.kraken_limits:main',
            'crypto_assets=madcc.entrypoints.crypto_assets:main',
        ],
    },
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
        'mock',
        'pytest-mock',
        'pytest-cov',
    ],
)
