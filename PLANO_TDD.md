# Plano de Trabalho — Frontend Django com TDD para o Sherlock

> **Equipe:** 6 pessoas organizadas em 3 duplas
> **Prazo:** **5 dias úteis** (sprint único)
> **Metodologia:** TDD (Red → Green → Refactor) em ciclos curtos
> **Repositório:** Monorepo (CLI atual + nova aplicação web no mesmo repo)
> **Escopo desta fase:** MVP funcional + testes unitários e de integração via TDD. E2E (Playwright) fica para fase posterior, mas o frontend já será preparado para ele.

> ⚠️ **Restrição de tempo:** com apenas 5 dias, o foco é **fluxo mínimo funcionando ponta a ponta com TDD**. Tudo marcado como _opcional_ só entra se sobrar tempo no Dia 5.

---

## 1. Visão geral e contexto

O Sherlock é uma CLI Python que busca a presença de um username em mais de 400 redes sociais. A lógica de negócio vive em `sherlock_project/` (módulos `sherlock.py`, `sites.py`, `result.py`, `notify.py`).

O objetivo deste plano é **construir uma interface web em Django** sobre essa lógica, **sem alterar a CLI existente**, usando TDD como prática obrigatória para todas as features novas. A meta secundária é deixar o frontend **pronto para receber testes E2E** numa fase futura, com seletores estáveis e fluxos previsíveis.

### Objetivos mensuráveis (realistas para 5 dias)
- Cobertura de testes ≥ **70%** no diretório `web/` (meta apertada considerando o prazo).
- 100% das features novas iniciam por um teste vermelho (verificado em PR).
- Pipeline CI **verde** em `master` em todos os merges.
- Zero alterações de comportamento em `sherlock_project/` (apenas leitura/consumo).
- MVP rodando local com `python manage.py runserver` ao fim do Dia 4.

### Fora de escopo nesta fase
- Autenticação de usuários.
- Banco em produção (SQLite em dev e CI).
- Deploy em provedor externo.
- Testes E2E (Playwright) — apenas preparação.
- **Cortado por prazo:** Docker/compose, paginação, filtro por site, HTMX streaming, pre-commit, badge de cobertura.

---

## 2. Stack técnica e justificativa

| Camada | Escolha | Por quê |
|---|---|---|
| Web framework | **Django 5.x** | Pedido do grupo. MTV nativo casa bem com TDD via `pytest-django`. |
| Templates | **Django Templates puro** | Sem HTMX nesta fase — busca síncrona (POST → renderiza resultados). Reduz superfície de teste. |
| Testes Python | **pytest + pytest-django + pytest-mock** | Mesma engine já usada em `tests/`. |
| Cobertura | **pytest-cov** | Relatório no terminal, sem extras. |
| Mocks de rede | **responses** | Isola `SherlockService` de chamadas HTTP reais. |
| Lint/format | **ruff** (só) | `black` cortado por prazo; `ruff format` cobre. |
| CI | **GitHub Actions** | Estendemos com 1 job só para `web/`. |
| E2E (fase futura) | **Playwright** | Apenas planejamento, não implementação. |

### Versões pinadas
```
Django==5.0.*
pytest==8.*
pytest-django==4.*
pytest-cov==5.*
pytest-mock==3.*
responses==0.25.*
ruff==0.6.*
```

---

## 3. Estrutura do monorepo

```
sherlock/
├── sherlock_project/              # CLI atual — INTOCADO
├── tests/                         # testes da CLI — INTOCADOS
├── web/                           # NOVO — aplicação Django
│   ├── manage.py
│   ├── pyproject.toml             # deps separadas do CLI
│   ├── pytest.ini                 # DJANGO_SETTINGS_MODULE=config.settings.test
│   ├── conftest.py                # fixtures compartilhadas
│   ├── config/                    # projeto Django
│   │   ├── __init__.py
│   │   ├── settings/
│   │   │   ├── base.py
│   │   │   ├── dev.py
│   │   │   └── test.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── apps/
│   │   ├── core/                  # Dupla 1
│   │   │   ├── services.py
│   │   │   ├── dtos.py
│   │   │   ├── exceptions.py
│   │   │   └── tests/
│   │   │       ├── test_service.py
│   │   │       └── test_dtos.py
│   │   ├── search/                # Dupla 2
│   │   │   ├── forms.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   ├── templates/search/
│   │   │   │   ├── index.html
│   │   │   │   └── results.html
│   │   │   └── tests/
│   │   │       ├── test_forms.py
│   │   │       └── test_views.py
│   │   └── export/                # Dupla 3 (sem DB nesta fase)
│   │       ├── exporters.py
│   │       ├── views.py
│   │       ├── urls.py
│   │       └── tests/
│   │           ├── test_exporters.py
│   │           └── test_views.py
│   ├── static/                    # CSS básico
│   └── templates/base.html
├── .github/workflows/
│   ├── ci-cli.yml                 # já existente
│   └── ci-web.yml                 # NOVO — Dupla 3
└── PLANO_TDD.md                   # este arquivo
```

---

## 4. Divisão de trabalho (3 duplas × 2 pessoas)

A divisão é por **vertical slice por camada**: cada dupla é dona de um app Django de ponta a ponta (código + testes + revisão).
Cross-review obrigatório: a dupla X só faz merge se a dupla Y aprovar — quebra silos e espalha conhecimento.

### Dupla 1 — **Core / Service Layer** (app `core`)

**Membros:** Victor Leandro, Pedro Henrique
**Missão:** Encapsular a chamada ao `sherlock_project` numa camada de serviço testável, com DTOs estáveis e tratamento de erros explícito.

#### Entregáveis
| Arquivo | Status |
|---------|--------|
| `apps/core/dtos.py` — `SiteResult`, `SearchRequest` | ✅ Concluído (commit `32f6974`) |
| `apps/core/exceptions.py` — `InvalidUsernameError`, `ServiceTimeoutError`, `UpstreamError` | ✅ Concluído (commit `32f6974`) |
| `apps/core/services.py` — `SherlockService.search` stub + import do `sherlock` | ✅ Stub criado (implementação real: Dia 2) |

#### Testes (cada um inicia vermelho)
| # | Teste | O que verifica | Status |
|---|---|---|---|
| 1 | `test_search_returns_results_for_known_user` | Mock de `sherlock_project` com 2 hits → 2 `SiteResult` com status correto. | 🔴 RED |
| 1b | `test_search_result_has_correct_url` | Complementar: SiteResult carrega a URL do perfil. | 🔴 RED |
| 2 | `test_search_rejects_empty_username` | `SearchRequest(username="")` levanta `InvalidUsernameError`. | 🔴 RED |
| 2b | `test_search_rejects_empty_username_without_network_call` | Validação ocorre antes de chamar `sherlock()`. | 🔴 RED |
| 3 | `test_search_rejects_username_with_invalid_chars` | Caracteres como `/`, espaço levantam `InvalidUsernameError`. | ⬜ Dia 3 |
| 4 | `test_search_propagates_timeout` | Upstream estoura → levanta `ServiceTimeoutError`. | ⬜ Dia 3 |
| 5 | `test_search_filters_by_sites` | `sites=["GitHub"]` → só aquele site é consultado (via mock). | ⬜ Dia 3 |
| 6 | `test_site_result_mapping_status_found` | `QueryStatus.CLAIMED` → `"found"`. | ⬜ Dia 2 |
| 7 | `test_site_result_mapping_status_not_found` | `QueryStatus.AVAILABLE` → `"not_found"`. | ⬜ Dia 2 |
| 8 | `test_service_does_not_perform_real_network_in_tests` | Sem mock o teste falha — protege a suíte de flakes. | ⬜ Dia 3 |

#### Definition of Done da Dupla 1
- 100% dos testes acima passando.
- `coverage` do app `core` ≥ 80%.
- Nenhum import de `requests` direto nas views — só passa pelo `SherlockService`.

---

### Dupla 2 — **Search (forms, views, templates)** (app `search`)

**Membros:** Pedro Teixeira, 
**Missão:** Fluxo de busca síncrono completo na web. Form de entrada, validação, página de resultados.

#### Entregáveis
- `apps/search/forms.py`
  - `SearchForm`: campo `username` (obrigatório, regex simples).
- `apps/search/views.py`
  - `index_view`: GET renderiza form vazio.
  - `results_view`: POST valida, dispara busca via `SherlockService`, renderiza `results.html` com a lista.
- `apps/search/templates/search/index.html`
  - Form com `data-testid="search-form"`, input `data-testid="username-input"`, botão `data-testid="submit-btn"`.
- `apps/search/templates/search/results.html`
  - Lista com `data-testid="results-list"`, cada item `data-testid="result-row"`.
  - Botões "Exportar CSV" / "Exportar JSON" apontando pro app `export` (acordar URL com Dupla 3).

#### Testes
| # | Teste | O que verifica | Status |
|---|---|---|---|
| 1 | `test_form_accepts_valid_username` | `SearchForm({"username":"john_doe"})` é válido. | 🔴 RED (forms.py vazio) |
| 2 | `test_form_rejects_empty_username` | Username vazio → form inválido com erro em `username`. | 🔴 RED |
| 3 | `test_form_rejects_invalid_chars` | `"jo hn"` → inválido. | 🔴 RED |
| 4 | `test_index_view_get_renders_form` | GET `/` retorna 200 e contém o form. | ❌ Pendente (Dia 1) |
| 5 | `test_results_view_post_invalid_returns_form_with_errors` | POST sem username → 200 + erro renderizado. | ⬜ Dia 2 |
| 6 | `test_results_view_post_valid_calls_service_with_username` | POST válido invoca `SherlockService.search` com `SearchRequest` esperado (mock). | ⬜ Dia 2 |
| 7 | `test_results_view_renders_hits` | Página de resultados mostra todos os `SiteResult` retornados pelo mock. | ⬜ Dia 3 |
| 8 | `test_results_view_renders_empty_state` | Zero resultados renderiza `data-testid="empty-state"`. | ⬜ Dia 3 |
| 9 | `test_results_view_renders_error_on_timeout` | Quando service levanta `ServiceTimeoutError`, página mostra `data-testid="error-state"`. | ⬜ Dia 3 |

#### Definition of Done da Dupla 2
- `data-testid` em todos os elementos interativos — base para o E2E futuro.
- Nenhum teste de view bate em rede real (mocks no `SherlockService`).
- `coverage` do app `search` ≥ 75%.

---

### Dupla 3 — **Export (in-memory) + Infra** (app `export` + tooling)

**Membros:** João Felipe
**Missão:** Exportar o resultado da busca atual em CSV/JSON (sem persistência) e manter o tooling (CI, lint, cobertura) que sustenta o TDD das outras duplas.

> ℹ️ Sem banco nesta fase. O export refaz a busca via `SherlockService` a partir do `username` na URL e devolve o arquivo direto. Persistência fica para o Pós-MVP.

#### Entregáveis — parte App
- `apps/export/exporters.py`
  - `to_csv(results: Iterable[SiteResult]) -> str`
  - `to_json(results: Iterable[SiteResult], username: str) -> str`
- `apps/export/views.py`
  - `export_view`: `GET /export/?username=x&format=csv|json` → faz busca via `SherlockService` e devolve `HttpResponse` com `Content-Type` apropriado e `Content-Disposition: attachment`.
- `apps/export/urls.py`: rota `/export/`.

#### Entregáveis — parte Infra
- Projeto Django inicializado (`web/manage.py`, `config/settings/{base,dev,test}.py`).
- `web/pytest.ini` apontando `DJANGO_SETTINGS_MODULE=config.settings.test`.
- `.github/workflows/ci-web.yml`:
  - Job único: instala deps, roda `ruff check`, roda `pytest --cov=apps --cov-fail-under=70`.
- `README.md` da raiz com seção curta "Rodando o web local" e "Rodando os testes do web".

#### Testes a escrever
| # | Teste | O que verifica |
|---|---|---|
| 1 | `test_to_csv_has_expected_headers` | `to_csv([...])` começa com `site_name,url,status`. |
| 2 | `test_to_csv_writes_one_row_per_result` | Lista com 3 resultados → 4 linhas (header + 3). |
| 3 | `test_to_csv_escapes_commas_in_fields` | Campo com vírgula é envolvido em aspas. |
| 4 | `test_to_json_is_valid_and_has_expected_shape` | `json.loads(to_json(...))` tem chaves `username`, `hits`. |
| 5 | `test_export_view_csv_returns_text_csv_content_type` | `?format=csv` → header `Content-Type: text/csv`. |
| 6 | `test_export_view_json_returns_application_json` | `?format=json` → header `Content-Type: application/json`. |
| 7 | `test_export_view_unknown_format_returns_400` | `?format=xml` → 400. |
| 8 | `test_export_view_missing_username_returns_400` | Sem `username` → 400. |

#### Definition of Done da Dupla 3
- CI rodando em todo PR e bloqueando merge se cobertura cair abaixo de 70%.
- `python manage.py runserver` sobe a aplicação em `http://localhost:8000`.
- `README.md` atualizado com instruções de execução.

---

## 5. Fluxo TDD obrigatório (Red → Green → Refactor)

Todo PR precisa demonstrar o ciclo. Roteiro:

1. **Issue** descreve o comportamento em forma de critério de aceite testável.
   *Exemplo:* "POST em `/` sem username deve retornar 200 e renderizar o erro `'Este campo é obrigatório.'`".
2. **PR draft "RED"**: contém apenas o teste novo, que **falha**. Commit message: `test: add failing test for empty username validation`.
3. **PR atualizado "GREEN"**: implementação mínima para o teste passar. Sem features extras. Commit: `feat: validate empty username on search form`.
4. **PR atualizado "REFACTOR"**: refatoração com todos os testes verdes. Commit: `refactor: extract username validator to forms.validators`.
5. **Code review** da dupla vizinha (ex.: Dupla 2 revisa PR da Dupla 1).
6. **Merge** em `master` via squash, com mensagem descritiva.

### Regras de PR
- Máximo **400 linhas** alteradas (excluindo migrations e snapshots) — força fatiar.
- Sempre ao menos **1 teste novo ou alterado**.
- CI verde obrigatório.
- Cross-review aprovado.

### Convenção de branches
- `feat/<app>-<descricao-curta>` — ex.: `feat/search-form-validation`.
- `fix/<app>-<descricao-curta>`.
- `chore/<descricao>` para tooling/infra.

### Convenção de commits (Conventional Commits)
- `test:` quando adiciona/altera teste.
- `feat:` nova funcionalidade.
- `fix:` correção.
- `refactor:` mudança sem alteração de comportamento.
- `chore:` infra, deps, build.

---

## 6. Cronograma — sprint único de 5 dias

> Cada dia tem um **marco verificável**. Se o marco do dia falhar, o próximo dia começa renegociando escopo, não acumulando dívida.

### Dia 1 — Setup e primeiros testes vermelhos

| Dupla | Entregas | Status |
|---|---|---|
| **D3** | Cria estrutura `web/`, `manage.py`, `settings/{base,dev,test}.py`, `pytest.ini`. | ✅ Concluído (commit `32f6974`) |
| **D3** | CI `ci-web.yml` rodando `pytest` vazio com sucesso em PR. | ❌ Pendente |
| **D1** | Escreve testes 1 e 2 vermelhos do `SherlockService` (sem implementação ainda). | ✅ Concluído — `web/apps/core/tests/test_service.py` (4 testes RED) |
| **D2** | Escreve testes 1, 2 e 3 vermelhos do `SearchForm`. | ✅ Concluído (commit `5570c85` + `928a6dc`) |
| **D2** | Escreve teste 4 vermelho do `index_view` (GET retorna 200). | ❌ Pendente |

**Marco Dia 1:** `pytest` roda no CI; cada dupla com pelo menos 2 testes vermelhos commitados.
**Status do marco:** 🟡 Quase — testes RED existem, CI ainda não.

### Dia 2 — Fluxo mínimo verde com mock

| Dupla | Entregas |
|---|---|
| **D1** | `SherlockService.search` devolve lista hardcoded de `SiteResult`. DTOs e exceções definidos. Testes 1, 2, 6, 7 verdes. |
| **D2** | `SearchForm` validando, `index_view` renderizando form, `results_view` chamando o service e renderizando. Testes 1–6 verdes. |
| **D3** | Esqueleto do app `export`: rota e view stub que devolve 200. Teste 5 verde. |

**Marco Dia 2:** abrir `/`, submeter form, ver lista mockada renderizada. Tudo via mocks.

### Dia 3 — Integração real com `sherlock_project`

| Dupla | Entregas |
|---|---|
| **D1** | `SherlockService` chamando `sherlock_project.sherlock.sherlock(...)` de verdade. Mapeamento `QueryStatus → status`. Tratamento de timeout. Testes 3, 4, 5, 8 verdes. |
| **D2** | Estados vazio e de erro renderizados. Testes 7, 8, 9 verdes. `data-testid` em tudo. |
| **D3** | `to_csv` e `to_json` implementados. Testes 1–4 verdes. |

**Marco Dia 3:** buscar username real (ex.: `torvalds`) e ver resultados reais. Sem export ainda.

### Dia 4 — Export e botões de download

| Dupla | Entregas |
|---|---|
| **D1** | Buffer/folga: cobre casos de borda que aparecerem; ajuda D2/D3. |
| **D2** | Botões "Exportar CSV/JSON" na página de resultados apontando pra `/export/?username=...&format=...`. |
| **D3** | `export_view` completo: chama `SherlockService`, escolhe exporter, devolve resposta com `Content-Disposition`. Testes 5, 6, 7, 8 verdes. |

**Marco Dia 4:** fluxo ponta a ponta funcionando — busca real + export CSV/JSON baixando arquivo.

### Dia 5 — Polimento, cobertura e documentação

| Dupla | Entregas |
|---|---|
| **D1** | Revisa cobertura do `core`, fecha gaps. |
| **D2** | Polimento visual mínimo (CSS básico, mensagens de erro amigáveis). |
| **D3** | CI com `--cov-fail-under=70` ativo. `README.md` atualizado. Apresentação do projeto preparada. |

**Marco Dia 5:** cobertura ≥ 70%, CI verde em `master`, README com instruções, apresentação ensaiada.

### Buffer e plano B
- Se o Dia 3 atrasar (integração com `sherlock_project` complica), **mantém o mock** e entrega Dia 4 com mock — a banca enxerga o fluxo e os testes; integração real vira Pós-MVP.
- Se o Dia 4 atrasar, corta JSON e entrega só CSV.

---

## 7. Definition of Done (geral)

Um item só está "pronto" quando:

- [ ] Tem teste(s) automatizados cobrindo o comportamento.
- [ ] Testes passam local **e** no CI.
- [ ] Cobertura do app afetado não regrediu.
- [ ] PR revisado e aprovado pela dupla vizinha.
- [ ] Sem warnings novos do `ruff`/`black`.
- [ ] Documentado em `README.md` se afeta uso/execução.

---

## 8. Métricas e qualidade

| Métrica | Meta | Onde se mede |
|---|---|---|
| Cobertura `web/` | ≥ 70% | `pytest --cov` no CI |
| Cobertura `apps/core` | ≥ 80% | `pytest --cov=apps/core` |
| Tempo da suíte | ≤ 15s local | `pytest --durations=10` |
| PRs sem teste novo | **0** | Revisão manual + check de CI |

---

## 9. Pós-MVP (enriquecimento, fora dos 5 dias)

Itens que **enriqueceriam o projeto** mas estão cortados do MVP por restrição de prazo. Ficam aqui documentados para retomada em fase posterior.

### 9.1 Persistência e histórico de buscas (app `history`)
**Por que enriquece:** Sherlock real demora 30s+ por consulta. Sem histórico, cada busca se perde — refazer dói. Com histórico, o usuário consulta tudo que já buscou, compara entre datas, e exporta sem refazer a busca.

**Escopo:**
- Modelo `SearchRun(id, username, created_at, duration_ms)` + `SiteHit(run, site_name, url, status)`.
- Hook em `search.views` que persiste após cada busca bem-sucedida.
- View `/history/` listando últimas buscas (paginadas).
- View `/history/<id>/` com detalhe e botões de export apontando para o run persistido (em vez de refazer busca).
- Migrar `apps/export` para consumir `SearchRun` em vez de refazer busca.

**Testes a adicionar:** persistência do run, listagem decrescente, paginação, export a partir de run salvo.

**Estimativa:** 1 sprint adicional (~5 dias) para 1 dupla.

### 9.2 Filtro por site / categoria
**Por que enriquece:** Sherlock tem 400+ sites; muitas vezes o usuário quer só GitHub + LinkedIn + X. Filtrar reduz tempo de busca de 30s para ~3s.

**Escopo:**
- Campo `sites` no `SearchForm` (multi-select com lista carregada de `SitesInformation`).
- Parâmetro `sites: list[str]` em `SearchRequest` (já previsto no DTO).
- UI: checkbox grid ou autocomplete.

**Estimativa:** 2 dias para 1 dupla.

### 9.3 Resultados parciais com HTMX
**Por que enriquece:** experiência do usuário muito melhor — em vez de esperar 30s olhando spinner, vê resultados aparecendo um a um.

**Escopo:**
- `django-htmx` instalado.
- `results_partial_view` que devolve fragmento.
- Polling ou SSE para empurrar hits conforme chegam.
- Adaptar `SherlockService.search` para devolver `Iterator` real (já previsto no contrato).

**Estimativa:** 2–3 dias para 1 dupla.

### 9.4 Containerização (Docker + compose)
**Por que enriquece:** roda em qualquer máquina sem precisar instalar Python/deps. Necessário pra deploy.

**Escopo:** `Dockerfile` para `web`, `docker-compose.yml` unindo `web` + (futuro) Postgres. ~meio dia.

### 9.5 Testes E2E com Playwright
**Por que enriquece:** garante que o fluxo do usuário funciona de verdade no navegador, não só nos mocks.

**Escopo:**
- `web/tests_e2e/` com Playwright.
- Cenários: busca feliz, busca com erro, export.
- Job de CI separado.
- Aproveita os `data-testid` que o MVP já entrega.

**Estimativa:** 2 dias para 1 dupla.

### 9.6 Outros itens nice-to-have
- Autenticação (login para histórico privado).
- Cache de resultados (mesmo username em < 1h reaproveita).
- Comparação entre buscas (mesmo username em datas diferentes).
- Tema escuro.
- API REST além da UI web (Django REST Framework).

---

## 10. Riscos e mitigações

| Risco | Probabilidade | Impacto | Mitigação |
|---|---|---|---|
| Dependência D3 atrasa e trava D1/D2 no Dia 1 | Alta | Alto | D3 tem **até o almoço do Dia 1** para entregar esqueleto + CI. Se atrasar, D1/D2 trabalham com `pytest` local enquanto D3 corre. |
| D1 ≠ D2: contrato do DTO muda no meio | Média | Alto | DTOs definidos e congelados no **Dia 1**. Mudança vira PR explícito com aviso. |
| Chamadas reais a redes sociais em testes geram flakes | Alta | Alto | Política: nenhum teste faz rede real. `responses` obrigatório em testes que tocam HTTP. |
| Integração com `sherlock_project` quebra no Dia 3 | Média | Alto | Plano B: manter mock e seguir com o mock no MVP. Integração real vira Pós-MVP. |
| Cobertura "cosmética" (testes que não testam comportamento) | Média | Médio | Revisão cruzada checa se o teste falha quando a implementação é quebrada. |
| Escopo crescer no meio (alguém querer adicionar feature) | Alta | Alto | Tudo extra vai pra seção 9 (Pós-MVP). Sem exceção. |

---

## 11. Preparação para E2E (Pós-MVP)

Mesmo sem implementar agora, o frontend já será desenhado para receber Playwright depois:

- Todos os elementos críticos terão `data-testid`.
- Rotas estáveis (`/`, `/export/`).
- Estados de loading/erro renderizados em DOM — facilita asserts.
- `manage.py runserver` inicia limpo em < 5s com `--noreload` para o CI futuro.

---

## 12. Convenções de código

- **Imports:** absolutos (`from apps.core.services import SherlockService`).
- **Type hints:** obrigatórios em código novo.
- **Tamanho de função:** máximo 30 linhas — se passar, extrair.
- **Sem `print`:** usar `logging`.
- **Templates:** indentação 2 espaços; blocos `{% %}` em linhas próprias.

---

## 13. Onboarding (reunião zero, antes do Dia 1)

1. Cada membro clona o repo e cria branch a partir de `master`.
2. **Dupla 3 entrega esqueleto até o almoço do Dia 1** (settings, manage.py, CI vazio).
3. Duplas 1 e 2 já chegam no Dia 1 com os testes vermelhos escritos (podem rodar em pytest local antes do CI existir).
4. Stand-up diário de 10 min — toda manhã, alinhamento e desbloqueio.
5. Retrospectiva curta no fim do Dia 5.

---

## 14. Anexos

### A. Mapeamento `QueryStatus` → status do DTO

| `QueryStatus` (CLI) | `SiteResult.status` (web) |
|---|---|
| `CLAIMED` | `"found"` |
| `AVAILABLE` | `"not_found"` |
| `UNKNOWN` | `"error"` |
| `WAF` / `ILLEGAL` | `"error"` |
| (timeout interno) | `"timeout"` |

### B. Estrutura de uma resposta exportada em JSON

```json
{
  "username": "john_doe",
  "hits": [
    {"site_name": "GitHub", "url": "https://github.com/john_doe", "status": "found"},
    {"site_name": "Reddit", "url": "https://reddit.com/user/john_doe", "status": "not_found"}
  ]
}
```

### C. Comandos úteis

```bash
# rodar testes do web
cd web && pytest

# cobertura
cd web && pytest --cov=apps --cov-report=term-missing

# subir local
cd web && python manage.py runserver

# lint
ruff check web/
```

---

**Última revisão:** 2026-05-28
**Responsável pela manutenção deste documento:** Dupla 3 (Infra)
