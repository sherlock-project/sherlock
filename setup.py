from setuptools import setup

# Current version of setup
def _get_version():
    return "%i.%i.%i" % (0, 3, 0)

# Requirements for the pypi
_requirements = [
    "requests",
    "grequests",
    "pyyaml",
    "requests_futures",
    "torrequest",
    "colorama"
]

# Packages part of setup
_packages = [
    "sherlock"
]

# Setup for the project
setup(
    name="thesherlock",
    version=_get_version(),
    description="Sherlock the username detective",
    long_description="""
        This scrapes and finds matching usernames over multiple HTTP hosts
    """,
    long_description_content_type="text/markdown",
    author="",
    author_email="",
    keywords="sherlock finder username pypi",
    url="https://github.com/TheYahya/sherlock/",
    license="MIT",
    packages=_packages,
    install_requires=_requirements,
    python_requires=">=3.5",
    classifiers=[
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3 :: Only"
    ]
)
