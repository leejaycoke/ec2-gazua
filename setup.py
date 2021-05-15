# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open("requirements.txt") as fp:
    requirements = [line.strip() for line in fp.readlines()]

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    mit_license = f.read()

setup(
    name='ec2-gazua',
    version='0.0.1',
    description='Easy accessing EC2 SSH through tmux',
    author='leejaycoke',
    author_email='leejaycoke@gmail.com',
    url='https://github.com/leejaycoke/ec2-gazua',
    long_description=readme,
    license=mit_license,
    install_requires=requirements,
    packages=find_packages(include=['ec2gazua'], exclude=['tests', 'image']),
    py_modules=['ec2_gz'],
    keywords=['ec2 ssh'],
    python_requires='>=3.7',
    package_data={},
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'ec2-gz = ec2_gz:main',
        ]
    },
    classifiers=[
        'Programming Language :: Python :: 3.7',
    ],
)
