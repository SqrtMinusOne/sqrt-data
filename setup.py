from setuptools import find_packages, setup

setup(
    name='smo_data',
    version='2.0.0',
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
    smo_data=smo_data.manage:cli
    ''')
