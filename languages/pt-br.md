<p align=center>

  <img src="https://user-images.githubusercontent.com/27065646/53551960-ae4dff80-3b3a-11e9-9075-cef786c69364.png"/>

  <br>
  <span>Procure contas de redes sociais pelo nome de usuário nas <a href="https://github.com/sherlock-project/sherlock/blob/master/sites.md">mídias sociais</a></span>
  <br>
  <a target="_blank" href="https://www.python.org/downloads/" title="Python version"><img src="https://img.shields.io/badge/python-%3E=_3.6-green.svg"></a>
  <a target="_blank" href="LICENSE" title="License: MIT"><img src="https://img.shields.io/badge/License-MIT-blue.svg"></a>
  <a target="_blank" href="https://github.com/sherlock-project/sherlock/actions" title="Test Status"><img src="https://github.com/sherlock-project/sherlock/workflows/Tests/badge.svg?branch=master"></a>
  <a target="_blank" href="https://github.com/sherlock-project/sherlock/actions" title="Nightly Tests"><img src="https://github.com/sherlock-project/sherlock/workflows/Nightly/badge.svg?branch=master"></a>
  <a target="_blank" href="https://twitter.com/intent/tweet?text=%F0%9F%94%8E%20Find%20usernames%20across%20social%20networks%20&url=https://github.com/sherlock-project/sherlock&hashtags=hacking,%20osint,%20bugbounty,%20reconnaissance" title="Share on Twitter"><img src="https://img.shields.io/twitter/url/http/shields.io.svg?style=social"></a>
  <a target="_blank" href="http://sherlock-project.github.io/"><img alt="Website" src="https://img.shields.io/website-up-down-green-red/http/sherlock-project.github.io/..svg"></a>
  <a target="_blank" href="https://hub.docker.com/r/theyahya/sherlock"><img alt="docker image" src="https://img.shields.io/docker/v/theyahya/sherlock"></a>
</p>

<p align="center">
<a href="https://asciinema.org/a/223115">
<img src="./images/sherlock_demo.gif"/>
</a>
</p>

<p align="center">
  <a href="#instalando">Instalação</a>
  &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;
  <a href="#uso">Uso</a>
  &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;
  <a href="#notas-do-docker">Notas do Docker</a>
  &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;
  <a href="#contribuindo">Contribuir</a>
  <br><br>
  <spam>Outros Idiomas: </spam>
  <br>
  <a href="./languages/pt-br.md">Portugês Brasileiro</a>
</p>

<p align="center">
<a href="https://asciinema.org/a/223115">
<img src="../images/sherlock_demo.gif"/>
</a>
</p>


## Instalando

```console
# clone o repositório
$ git clone https://github.com/sherlock-project/sherlock.git

# mude o diretório atual para o sherlock
$ cd sherlock

# instalando os requisitos
$ python3 -m pip install -r requirements.txt
```

## Uso

```console
$ python3 sherlock --help
usage: sherlock [-h] [--version] [--verbose] [--folderoutput FOLDEROUTPUT]
                [--output OUTPUT] [--tor] [--unique-tor] [--csv]
                [--site SITE_NAME] [--proxy PROXY_URL] [--json JSON_FILE]
                [--timeout TIMEOUT] [--print-all] [--print-found] [--no-color]
                [--browse] [--local]
                USERNAMES [USERNAMES ...]

Sherlock: Find Usernames Across Social Networks (Version 0.14.2)

argumentos posicionais:
  USERNAMES             Um ou mais nomes de usuário a serem verificados nas redes sociais.

argumentos opcionais:
  -h, --help            Mostra esta mensagem de ajuda e fecha.
  --version             Exibe informações de versão e suas dependências.
  --verbose, -v, -d, --debug
                        Exibe informações extras de depuração.
  --folderoutput FOLDEROUTPUT, -fo FOLDEROUTPUT
                        Se estiver usando vários nomes de usuário, a saída dos resultados será
                        salva em uma pasta.
  --output OUTPUT, -o OUTPUT
                        Se estiver usando apenas um nome de usuário, a saída do resultado será salva
                        neste arquivo.
  --tor, -t             Faz requisições pelo Tor (aumenta o tempo de execução) requer que o Tor seja
                        instalado e dentro do caminho do sistema.
  --unique-tor, -u      Faz solicitações pelo Tor com o novo circuito Tor após cada solicitação;
                        aumenta o tempo de execução; requer que o Tor esteja instalado e
                        dentro do caminho do sistema.
  --csv                 Cria um arquivo de valores separados por vírgula (CSV).
  --xlsx                Cria o arquivo padrão para planilhas do Microsoft Excel(xslx).
  --site SITE_NAME      Limita a análise apenas aos sites listados. Adicione várias opções para
                        especificar mais de um site.
  --proxy PROXY_URL, -p PROXY_URL
                        Faz solicitações por meio de um proxy. por exemplo: socks5://127.0.0.1:1080
  --json JSON_FILE, -j JSON_FILE
                        Carrega dados de um arquivo JSON ou de um arquivo JSON online válido.
  --timeout TIMEOUT     Tempo (em segundos) para aguardar resposta às solicitações (Padrão: 60).
  --print-all           Retorna sites onde o nome de usuário não foi encontrado.
  --print-found         Retorna sites onde o nome de usuário foi encontrado.
  --no-color            Deixa a saída do terminal sem cores.
  --browse, -b          Procura todos os resultados no navegador padrão.
  --local, -l           Força o uso do arquivo data.json local.
```

Para pesquisar apenas um usuário:
```
python3 sherlock user123
```

Para pesquisar mais de um usuário:
```
python3 sherlock user1 user2 user3
```

As contas encontradas serão armazenadas em um arquivo de texto individual com o nome de usuário correspondente (por exemplo, ```user123.txt```).

## Notas do Anaconda (Windows)

Se você estiver usando o Anaconda no Windows, usar 'python3' pode não funcionar. Use 'python' em vez disso.

## Notas do Docker

Se o docker estiver instalado, você poderá criar uma imagem e executá-la como um contêiner.

```
docker build -t mysherlock-image .
```

Depois que a imagem é criada, o sherlock pode ser executado usando o seguinte:

```
docker run --rm -t mysherlock-image user123
```

A opção ```--rm``` remove o sistema de arquivos do contêiner na conclusão para evitar o acúmulo de lixo. Consulte: https://docs.docker.com/engine/reference/run/#clean-up---rm

A opção ```-t``` aloca um pseudo-TTY que permite saída colorida. Consulte: https://docs.docker.com/engine/reference/run/#foreground

Use o seguinte comando para acessar os resultados salvos:

```
docker run --rm -t -v "$PWD/results:/opt/sherlock/results" mysherlock-image -o /opt/sherlock/results/text.txt user123
```

As opções ```-v "$PWD/results:/opt/sherlock/results"``` dizem ao docker para criar (ou usar) a pasta `results` m e montá-lo em `/opt/sherlock/results` no contêiner docker. A opção `-o /opt/sherlock/results/text.txt` diz ao `sherlock` para produzir o resultado.

Ou você pode usar o "Docker Hub" para executar o `sherlock`:
```
docker run theyahya/sherlock user123
```

### Uso do `docker-compose`

Você pode usar o arquivo `docker-compose.yml` do repositório e usar este comando:

```
docker-compose run sherlock -o /opt/sherlock/results/text.txt user123
```

## Contribuindo
Adoraríamos que você nos ajudasse com o desenvolvimento de Sherlock. Cada contribuição é muito valorizada!

Aqui estão algumas coisas em que gostaríamos de sua ajuda:
- Adição de novo suporte ao site ¹
- Trazendo de volta o suporte do site de [sites que foram removidos](removed_sites.md) no passado devido a falsos positivos

[1] Por favor, veja a entrada do Wiki em [adicionar novos sites](https://github.com/sherlock-project/sherlock/wiki/Adding-Sites-To-Sherlock)
para entender as questões.

## Testes

Obrigado por contribuir com Sherlock!

Antes de criar um pull request com o novo desenvolvimento, execute os testes
para garantir que tudo esteja funcionando perfeitamente. Também seria uma boa ideia fazer os testes
antes de iniciar o desenvolvimento para distinguir problemas entre seu
ambiente e o software Sherlock.

A linha de comando a seguir executa todos os testes para o Sherlock.
Este comando oculta o texto de progresso que Sherlock normalmente
retorna e, em vez disso, mostra a saída detalhada dos testes.

```
$ cd sherlock/sherlock
$ python3 -m unittest tests.all --verbose
```

Observe que atualmente temos 100% de cobertura nos testes. Infelizmente, alguns
dos sites que Sherlock verifica nem sempre são confiáveis, por isso é comum
obter problemas de resposta. Qualquer problemas na conexão aparecerão como
avisos nos testes em vez de erros reais.

Se alguns sites estiverem falhando devido a problemas de conexão (site está fora do ar, em manutenção, etc)
você pode excluí-los dos testes criando um arquivo `tests/.excluded_sites` com uma
lista de sites a serem ignorados (um nome de site por linha).

## Stargazers ao longo do tempo

[![Stargazers over time](https://starchart.cc/sherlock-project/sherlock.svg)](https://starchart.cc/sherlock-project/sherlock)

## Licença

MIT © Sherlock Project<br/>
Original Creator - [Siddharth Dushantha](https://github.com/sdushantha)
