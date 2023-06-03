import os

from setuptools import find_namespace_packages, setup  # type: ignore

CWD = os.path.abspath(os.path.dirname(__file__))
ABOUT = {}
with open(os.path.join(CWD, "sherlock", "__version__.py"), "r") as f:
    # pylint: disable=exec-used
    exec(f.read(), ABOUT)

with open("README.md", "r") as f:
    README = f.read()

setup(
    name=ABOUT["__title__"],
    version=ABOUT["__version__"],
    description=ABOUT["__description__"],
    long_description=README,
    long_description_content_type="text/markdown",
    author=ABOUT["__author__"],
    url=ABOUT["__url__"],
    packages=find_namespace_packages(include=["sherlock.*"]),
    include_package_data=True,
    license=ABOUT["__license__"],
    entry_points={
        "console_scripts": [
            "sherlock=sherlock.sherlock:main",
        ],
    },
)
