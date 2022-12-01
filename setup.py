# [[file:org/core-new.org::*setup.py for agent][setup.py for agent:1]]
from setuptools import find_packages, setup

setup(
    name='sqrt_data_agent',
    version='3.0.0',
    description='Agent for sqrt-data',
    author='SqrtMinusOne',
    author_email='thexcloud@gmail.com',
    packages=find_packages(exclude=['sqrt_data_service']),
    install_requires=[
        'pandas>=1.4.2',
        'numpy>=1.21.6',
        'requests>=2.27.1',
        'furl>=2.1.3',
        'dynaconf>=3.1.7',
        'python-mpd2>=3.0.4',
        'python-dateutil>=2.8.2',
    ],
    entry_points='''
    [console_scripts]
    sqrt_data_agent_mpd=sqrt_data_agent.mpd:main
    sqrt_data_agent_sync=sqrt_data_agent.sync:main
    '''
)
# setup.py for agent:1 ends here
