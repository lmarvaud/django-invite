"""
setup

Created by lmarvaud on 02/11/2018
"""
from setuptools import setup, find_packages

setup(
    name='django_invite',
    version='0.1.0',
    description='Django application to help managing guest and invitation',
    author='Leni Marvaud',
    author_email='24732919+lmarvaud@users.noreply.github.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Plugins',
        'Environment :: Web Environment',
        'Framework :: Django :: 2.0',
        'Framework :: Django :: 2.1',
        'Framework :: Django :: 2.2',
        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: French',
        'Operating System :: MacOS :: MacOS X',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Communications :: Email',
        'Topic :: Communications :: Email :: Address Book',
        'Topic :: Communications :: Email :: Mailing List Servers',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    keywords='django email invitation',
    packages=find_packages(exclude=['demo']),
    include_package_data=True,
    install_requires=[
        'django>=2.0'
    ],
    dependency_links=[
        'django>=2.0'
    ],
)
