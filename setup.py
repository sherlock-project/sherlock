from setuptools import setup
from sherlock import __version__, module_name

setup(
    name = 'sherlock',
    version = __version__,
    description = module_name,
    packages = ['sherlock'],
    entry_points = {
        'console_scripts': [
            'sherlock = sherlock.__main__:main'
        ]
    },
    package_dir={'sherlock': 'sherlock'},
    package_data={'sherlock' : ['data.json']},
    install_requires=[
        "requests",
        "torrequest"
    ]
)
