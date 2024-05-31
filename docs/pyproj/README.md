<!-- This README should be a mini version at all times for use on pypi -->

<p align=center>
  <br>
  <a href="https://sherlock-project.github.io/" target="_blank"><img src="https://user-images.githubusercontent.com/27065646/53551960-ae4dff80-3b3a-11e9-9075-cef786c69364.png"/></a>
  <br>
  <span>Hunt down social media accounts by username across <a href="https://github.com/sherlock-project/sherlock/blob/master/sites.md">social networks</a></span>
  <br>
  <span>Additional documentation can be found on our <a href="https://github.com/sherlock-project/sherlock/">GitHub repository</a></span>
  <br>
</p>

<p align="center">
<img width="70%" height="70%" src="https://user-images.githubusercontent.com/27065646/219638267-a5e11090-aa6e-4e77-87f7-0e95f6ad5978.png"/>
</a>
</p>

## Usage

```console
$ sherlock --help
usage: sherlock [-h] [--version] [--verbose] [--folderoutput FOLDEROUTPUT]
                [--output OUTPUT] [--tor] [--unique-tor] [--csv] [--xlsx]
                [--site SITE_NAME] [--proxy PROXY_URL] [--json JSON_FILE]
                [--timeout TIMEOUT] [--print-all] [--print-found] [--no-color]
                [--browse] [--local] [--nsfw]
                USERNAMES [USERNAMES ...]
```

To search for only one user:
```bash
$ sherlock user123
```

To search for more than one user:
```bash
$ sherlock user1 user2 user3
```

## Star History

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=sherlock-project/sherlock&type=Date&theme=dark" />
  <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=sherlock-project/sherlock&type=Date" />
  <img alt="Sherlock Project Star History Chart" src="https://api.star-history.com/svg?repos=sherlock-project/sherlock&type=Date" />
</picture>
