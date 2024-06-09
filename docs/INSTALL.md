<p align=center>
  <br>
  <a href="https://sherlock-project.github.io/" target="_blank"><img src="https://user-images.githubusercontent.com/27065646/53551960-ae4dff80-3b3a-11e9-9075-cef786c69364.png"/></a>
  <br>
</p>

<p align="center">
  <strong><a href="https://github.com/sherlock-project/sherlock">Home</a></strong>
  &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;
  <strong><a href="#">Installation</a></strong>
  &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;
  <a href="https://github.com/sherlock-project/sherlock#usage">Usage</a>
  &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;
  <a href="#docker">Docker</a>
  &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;
  <a href="https://github.com/sherlock-project/sherlock/docs/CONTRIBUTING.md">Contributing</a>
</p>



# Alternative install methods

1. __[Python package](#python)__
    1. [Build from source](#build-and-install-package-from-source)
1. __[Docker Container](#docker)__
    1. [via Docker Hub (one off)](#docker)
    1. [via Docker Hub (compose)](#using-compose)
    1. [Local image with Dockerfile](#build-image-from-source-alternative-to-docker-hub)

<h2>
Python
<a href="https://pypi.org/project/sherlock-project/"><img align="right" alt="PyPI - Version" src="https://img.shields.io/pypi/v/sherlock-project?style=for-the-badge&logo=PyPI&label=PyPI&color=darkgreen"></a>
</h2>

```bash
# pipx is recommended, but pip may suffice if pipx is unavailable
pipx install sherlock-project
```

### Build live package from source (useful for contributors)

Building an editable (or live) package links the entry point to your current directory, rather than to the standard install location. This is often useful when working with the code base, as changes are reflected immediately without reinstallation.

Note that the version number will be 0.0.0 for pipx local builds unless manually changed in the pyproject file (it will prompt the user for an update).

```bash
# Assumes repository cloned, and current working directory is repository root
pipx install -e .
```

### Run package from source (without installing)

If you'd rather not install directly to your system, you can import the module at runtime with `-m`.

```bash
# Assumes repository cloned, and current working directory is repository root
python3 -m sherlock user123 user789
```

<h2>
Docker
<a href="https://hub.docker.com/r/sherlock/sherlock"><img align="right" alt="Docker Image Version" src="https://img.shields.io/docker/v/sherlock/sherlock?sort=semver&style=for-the-badge&logo=docker&label=Docker&color=darkgreen"></a>
</h2>

> [!NOTE]
> Sherlock doesn't yet have context detection. It's recommended that Docker containers be ran with option `-o /opt/sherlock/results/{user123}.txt` (replace {user123}) when an output file is desired at the mounted volume (as seen in the compose).
>
> This has no effect on stdout, which functions as expected out of the box.

```bash
# One-off searches
docker run --rm -t sherlock/sherlock user123

# If you need to save the output file... (modify as needed)
# Output file will land in ${pwd}/results
docker run --rm -t -v "$PWD/results:/opt/sherlock/results" sherlock/sherlock -o /opt/sherlock/results/text.txt user123
```

```bash
# At any time, you may update the image via this command
docker pull sherlock/sherlock
```

### Using compose

```yml
version: "3"
services:
  sherlock:
    container_name: sherlock
    image: sherlock/sherlock
    volumes:
      - ./sherlock/:/opt/sherlock/results/
```

```bash
docker compose run sherlock user123
```

### Build image from source (useful for contributors)

```bash
# Assumes ${pwd} is repository root
docker build -t sherlock .
docker run --rm -t sherlock user123
```
