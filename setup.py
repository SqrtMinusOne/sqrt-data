# [[file:org/index.org::*setup.py and requirements][setup.py and requirements:1]]
from setuptools import find_packages, setup

setup(
    name='sqrt_data',
    version='2.0.1',
    description=
    'A collection of scripts to gather various data from my machines and store it on my VPS',
    author='SqrtMinusOne',
    author_email='thexcloud@gmail.com',
    packages=find_packages(),
    install_requires=[
        'pandas', 'numpy', 'click', 'inquirer', 'python-mpd2', 'sqlalchemy',
        'psycopg2-binary', 'requests', 'tqdm', 'beautifulsoup4'
    ],
    entry_points='''
    [console_scripts]
    sqrt_data=sqrt_data.manage:cli
    ''')
# setup.py and requirements:1 ends here
