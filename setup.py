from setuptools import setup, find_packages

setup(
    name='redscraping', # The pip install name
    version='1.0.2',
    packages=find_packages(),
    install_requires=[
        'click',
        'selenium',
        'webdriver-manager',
        'pandas',
        'gspread',
        'google-auth-oauthlib',
        'openpyxl',
        'colorama',
        'rich',
        'beautifulsoup4',
        'requests',
        'aiohttp',
        'google-api-python-client',
        'curl_cffi',
        'google-genai'

    ],
    entry_points='''
        [console_scripts]
        redscrape=redscraping_core.cli:main_cli
    ''',
)