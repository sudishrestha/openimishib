import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='openimis-be-api_fhir_r4',
    version='1.0.0',
    packages=find_packages(),
    include_package_data=True,
    license='GNU AGPL v3',
    description='The openIMIS Backend FHIR R4 API reference module.',
    long_description=README,
    long_description_content_type='text/markdown',
    url='https://openimis.org/',
    author='Faris Ahmetasevic',
    author_email='faris.ahmetasevic@hotmail.com',
    install_requires=[
        'django',
        'django-db-signals',
        'djangorestframework',
        'fhir.resources==6.2.0b3',
        'openimis-be-core',
        'openimis-be-insuree',
        'openimis-be-location',
        'openimis-be-claim',
        'openimis-be-policy',
        'openimis-be-policyholder'
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 2.1',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)