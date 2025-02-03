[build-system]
requires = [ "poetry-core>=1.2.0" ]
build-backend = "poetry.core.masonry.api"
# poetry-core 1.8 not available in .fc39. Can upgrade to 1.8.0 at .fc39 EOL

[tool.poetry-version-plugin]
source = "init"

[tool.poetry]
name = "sherlock-project"
# single source of truth for version is __init__.py
version = "0"
description = "Hunt down social media accounts by username across social networks"
license = "MIT"
authors = [
    "Siddharth Dushantha <siddharth.dushantha@gmail.com>"
]
maintainers = [
    "Paul Pfeister <code@pfeister.dev>",
    "Matheus Felipe <matheusfelipeog@protonmail.com>",
    "Sondre Karlsen Dyrnes <sondre@villdyr.no>"
]
readme = "docs/pyproject/README.md"
packages = [ { include = "sherlock_project"} ]
keywords = [ "osint", "reconnaissance", "information gathering" ]
classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Developers",
    "Intended Audience :: Information Technology",
    "Natural Language :: English",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Topic :: Security"
]
homepage = "https://sherlockproject.xyz/"
repository = "https://github.com/sherlock-project/sherlock"


[tool.poetry.urls]
"Bug Tracker" = "https://github.com/sherlock-project/sherlock/issues"

[tool.poetry.dependencies]
python = "^3.9"
certifi = ">=2019.6.16"
colorama = "^0.4.1"
PySocks = "^1.7.0"
requests = "^2.22.0"
requests-futures = "^1.0.0"
stem = "^1.8.0"
torrequest = "^0.1.0"
pandas = "^2.2.1"
openpyxl = "^3.0.10"

[tool.poetry.extras]
tor = ["torrequest"]

[tool.poetry.group.dev.dependencies]
jsonschema = "^4.0.0"

[tool.poetry.scripts]
sherlock = 'sherlock_project.sherlock:main'
