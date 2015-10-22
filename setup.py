# try:
from setuptools import setup, find_packages 
# except ImportError:
#     from distutils.core import setup

setup(
    name='svven-poller',
    version='0.1',
    author='Alexandru Stanciu',
    author_email='ducu@svven.com',
    packages=find_packages(),
    url='https://bitbucket.org/svven/poller',
    description='Background worker component for system data input',
    install_requires=[
        'SQLAlchemy>=0.9.8',
        'rq>=0.4.6',
        'svven-aggregator>=0.1',
    ],
)