from setuptools import setup, find_packages

setup(
    name='redscraping', # The pip install name
    version='1.0.1',
    packages=find_packages(),
    install_requires=[
        'click',
        'selenium',
        'webdriver-manager',
        'pandas',
        'gspread',
        'google-auth-oauthlib',
        'openpyxl',
        'colorama'
    ],
    entry_points='''
        [console_scripts]
        redscrape=redscraping_core.cli:main_cli
    ''',
)