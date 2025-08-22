# Mapping.md — Plano Mestre do Hermes

> Documento de organização **zero→um**: tudo o que precisa ser feito, em ordem, com papéis, contratos, entregáveis, riscos e planos B/C.

---

## 🧭 Pré-ambulo (5 passos solicitados)

**ENTENDER.** Construir um sistema que receba códigos de ações, colete e padronize dados (geral/setor/empresa), gere previsões e métricas, compile tudo em **Ações Analisadas**, monte/ajuste uma **carteira**, submeta a um **Conselho** e entregue um **PDF** explicável — com UI gamificada (Cidade‑IA).
**ANALISAR.** Componentes: Idealizador (UI), Pesquisadores (4 frentes), Analista (Forecast), **Gênio (Compilador)**, **Banco de Dados (hub/monitor)**, Montador, Conselho, Escrivão; além de: ferramentas (Pesquisa, Forecast, Alocação, Métricas, NLP, Report), contratos, storage, UI, CI/CD.
**RACIOCINAR.** Modularizar em **apps** (serviços) + **packages** (bibliotecas); usar **contratos únicos**; o **BD** emite eventos; o Gênio **não orquestra** — só compila; UI consome eventos e artefatos.
**SINTETIZAR.** Monorepo com apps/ (serviços), packages/ (libs), data/ (artefatos/logs), assets/, configs/, scripts/, docs/, tests/. Fluxo dirigido por **completude no BD**.
**CONCLUIR.** Abaixo segue o mapa completo de mecânicas, tarefas e critérios de pronto, mais **Plano B** (reduzido) e **Plano C** (mínimo viável).

---

## 1) Visão de fluxo (papéis e fronteiras)

**Entrada:** Idealizador/Cliente (UI) envia `tickers[]` + preset.
**Pesquisa (4 frentes):** Relatórios (RI/filings), Notícias, ESG, **Datasets**. Todos pesquisam **geral, setor, empresa**, sempre **checando BD/TTL** antes de ir às APIs.
**Analista:** recebe **dataset padronizado** e roda **Forecast Tool** (modelos, backtesting, métricas).
**Gênio (Compilador):** agrega **insumos semânticos + resultados do Analista + sentimento próprio + código** e gera **Ação Analisada** (formato único).
**BD (Monitor):** quando todas as ações do run estão `COMPILED`, dispara **Montador**.
**Montador:** carteira base (alocação) + **ajustes pequenos por sentimento** (justificados).
**Conselho (C/M/A):** aprova/refaz; se refazer → volta ao Montador com diretrizes.
**Escrivão:** gera **PDF/JSON** final.
**UI:** Vila (anima eventos) + Painel (Atividades/Arquivos).

Estados por **ticker**: `PENDING → RESEARCH_DONE → ANALYST_DONE → COMPILED`
Estados por **run**: `NEW → TICKERS_IN_PROGRESS → ALL_COMPILED → PORTFOLIO_DRAFT → COUNCIL → APPROVED → SUMMARY_READY`

---

## 2) Mecânicas — passo a passo (com entregáveis)

### 2.1 Idealizador

* **Input UI:** lista (auto‑pick ou manual) + preset.
* **Ação:** `POST /runs/start` → grava `runs` e `tickers` no BD.
* **Entrega:** registro em `runs(id, preset, tickers[], status=NEW)`.

### 2.2 Pesquisa (4 frentes) — *sempre checar BD/TTL*

* **Relatórios (RI/Filings):** baixa apresentações, press releases, ITR/DFP/10‑K/10‑Q; extrai texto; salva snapshot.
* **Notícias:** coleta RSS/GDELT; limpa HTML; deduplica; classifica por empresa/setor; sentimento inicial.
* **ESG:** busca relatórios de sustentabilidade/GRI; extrai métricas (scope 1–3 etc.).
* **Datasets:** monta séries **padronizadas** (macro, setoriais, empresa) + preços ajustados.
* **Regra TTL:** global/setor (30–90d), empresa (sempre atualizar), preços diários (24h), ESG/filings (90–180d).
* **Entrega:** `ResearchBundle` (relatórios/notícias/ESG → **Gênio**) e `Dataset` (→ **Analista**).
* **Critérios de pronto:** snapshots salvos; metadados `{license, access_level, source_url, checksum}`; dedupe ok.

### 2.3 Analista (Forecast & métricas)

* **Input:** `Dataset` padronizado (preços + regressoras).
* **Ação:** backtesting (expanding|rolling, 5 folds, passo 3m), métrica primária **sMAPE**, blend Top‑K (NNLS), risco local (vol, maxDD; opcional TE/CVaR).
* **Entrega:** `ForecastResult` `{leaderboard[], blend{}, forecast_path, metrics{}}`.
* **Critérios:** validação sem fuga temporal; DM‑test opcional; artefatos em `data/artifacts/{run_id}/forecast/`.

### 2.4 Gênio (Compilador)

* **Input:** insumos semânticos (relatórios/notícias/ESG) + `ForecastResult` + **sentimento agregado** + **código do ticker**.
* **Ação:** normaliza, ranqueia evidências, anexa links/snapshots, produz **Ação Analisada**.
* **Entrega:** `AcaoAnalisada` em `compiled_actions` + arquivo JSON em `artifacts/{run_id}/compiled/`.
* **Critérios:** todos os campos presentes; citações/snapshots ok; `compiled=true`.

### 2.5 BD (Monitor de completude)

* **Ação:** trigger/worker conta `compiled_actions` por run; ao atingir `runs.total_tickers`, grava `portfolio_requests`.
* **Entrega:** `PortfolioBuildRequest` para o Montador.
* **Critérios:** idempotência (evitar múltiplos disparos); NOTIFY `portfolio_ready`.

### 2.6 Montador de Carteira + Ajuste por Sentimento

* **Input:** `AcaoAnalisada[]` do run + limites de risco/caps (do preset).
* **Ação:** otimização (MV/BL/RP/CVaR); gera **carteira base**; aplica **ajustes pequenos** (±1 pp por ativo, configurável) com **justificativas** ligadas a eventos/sentimento.
* **Entrega:** `PortfolioDraft` → `PortfolioFinal`.
* **Critérios:** restrições satisfeitas; justificativas registradas; artefatos em `artifacts/{run_id}/portfolio/`.

### 2.7 Conselho (C/M/A)

* **Input:** `PortfolioFinal` + métricas/exposições.
* **Ação:** votar **Aprovar**/**Refazer** com comentários objetivos (limites ou metas).
* **Loop:** se **Refazer**, BD cria `PortfolioRebuildRequest` com diretrizes → volta ao Montador.
* **Entrega:** `CouncilDecision` em `council_votes` + resumo por perfil.
* **Critérios:** quórum e maioria simples; logs por run.

### 2.8 Escrivão (Resumo)

* **Input:** análises compiladas + carteira aprovada + decisão do Conselho.
* **Ação:** gerar **PDF** (e JSON) com narrativa, figuras e **fontes**.
* **Entrega:** `Summary{pdf_path, json_path}` em `artifacts/{run_id}/report/`.
* **Critérios:** disclaimers; links e snapshots; tamanho e clareza.

### 2.9 UI (Cidade‑IA)

* **Input:** eventos por `run_id` (do BD ou API relay) + links de artefatos.
* **Ação:** anima agentes por nós (A\*), exibe log **Atividades** e **Arquivos**; modos **tempo real** ou **cinemático** (45–60s).
* **Entrega:** usabilidade e visual; **sem travas** no palco.

---

## 3) Contratos (fonte da verdade)

* `analysis_request.schema.json` — `{run_id, tickers[], preset, options}`
* `research_bundle.schema.json` — notícias/filings/ESG por ticker (metadados com licença/snapshot)
* `dataset.schema.json` — preços/regressoras padronizados (coverage, freq, checksum)
* `forecast_result.schema.json` — leaderboard, blend, métricas, paths
* `acao_analisada.schema.json` — fundamentals{}, esg{}, forecast{}, sentiment{}, risks{}, insights[]
* `portfolio_build_request.schema.json` — objetivo, limites, caps
* `portfolio_draft.schema.json` — weights0{}, metrics{}, exposições{}
* `portfolio_final.schema.json` — weights{}, ajustes_sentimento[], justificativas[]
* `council_decision.schema.json` — votes[], status, comments[]
* `summary.schema.json` — pdf_path, json_path, toc, sources

> **Regra:** Schemas geram automaticamente **Pydantic** (Python) e **tipos TS** (frontend).

---

## 4) Banco de dados & storage

**Tabelas mínimas**

```
runs, research_bundles, datasets, forecasts,
compiled_actions, portfolio_requests, portfolios,
council_votes, summaries, events
```

**Triggers/NOTIFY:** `compiled_actions` → `portfolio_requests` quando todos compilados.
**Storage:** MinIO/S3 para blobs (PDF, HTML, Parquet); Redis para cache TTL; Postgres para metadados/NOTIFY.
**Logs:** `data/logs/{run_id}.jsonl` (eventos estruturados, replayável na UI).

---

## 5) Ferramentas & APIs (principais)

* **Preços:** B3 (licenciado) | Fallback: yfinance/Stooq.
* **Filings/Relatórios:** CVM Dados Abertos + sites de RI | SEC EDGAR (EUA).
* **Macro:** BCB/SGS, IBGE/SIDRA | FRED, World Bank.
* **Notícias:** RSS/Atom (Reuters/Valor/FT…) | GDELT.
* **ESG:** páginas de Sustentabilidade/RI | GRI (quando aplicável).

> Sempre gravar `license` e `access_level` nos metadados; snapshots obrigatórios.

---

## 6) Observabilidade, erros e qualidade

* **Logs JSON** por serviço (structlog), com `run_id` e `stage`.
* **Métricas Prometheus**: duração por etapa, erros por 100 runs, cache hit‑rate.
* **Taxonomia de erros:** `E.NET.*`, `E.HTTP.*`, `E.PARSE.*`, `E.MODEL.*`, `E.DATA.*`, `E.LICENSE.*`.
* **Resiliência:** retry exponencial c/ jitter; respeito a `Retry‑After`; fallback de fontes.
* **DQ (data quality):** gaps/splits, staleness, dedupe (sha256+simhash), *point‑in‑time*.

---

## 7) Frontend (componentes e estados)

* **LeftPanel:** presets, auto‑pick (N) ou lista manual, real‑time toggle, Start.
* **VillageStage (Pixi):** tilemap, câmera (zoom/pan), A\*, sprites dos agentes, balões de fala.
* **RightPanel:** **Atividades** (log chat‑like), **Arquivos** (artefatos com preview).
* **AgentDock:** status por agente (Dormindo/Andando/Trabalhando/Comunicando/Erro).
* **Stores (Zustand):** `UIConfig`, `RunState`, `VillageState`.
* **Eventos WS:** `MOVE_TO`, `TASK_CHANGE`, `FILE_SAVED`, `MODEL_FINISHED`, etc.

---

## 8) Infra, CI/CD e produtividade

* **Docker Compose**: Postgres, Redis, MinIO, API, workers, UI.
* **CI**: lint (ESLint/Ruff), testes (Jest/Pytest), validação de Schemas, build UI.
* **Scripts:** `dev.sh`, `seed.py`, `run_demo.py`, `export_report.py`.
* **Segredos:** `.env` + vault (quando em produção).
* **Compliance:** disclaimers no PDF; retenção de artefatos; política de licença.

---

## 9) Plano de execução (MVP → Completo)

### Fase 1 — MVP (4–6 semanas)

1. **Contracts** completos (JSON Schemas gerando TS/Pydantic).
2. **API gateway** (start run, relay WS, serve artifacts).
3. **Pesquisa (datasets+notícias+relatórios)** com TTL e snapshots.
4. **Analista/Forecast** (SARIMAX/ETS/XGB; backtesting + blend).
5. **Gênio (Compilador)** de Ação Analisada.
6. **BD‑Monitor** + **Montador** (MV; caps) + **Ajuste Sentimental** (±1 pp).
7. **Conselho** (regras simples) e **Escrivão** (PDF curto).
8. **UI vila** (tempo cinemático) + painel de logs/arquivos.
   **DoD:** run reprodutível fim‑a‑fim com 2–3 tickers.

### Fase 2 — Versão completa (6–10 semanas)

1. Mais modelos (VAR/BVAR, BL/CVaR), ESG parser estruturado.
2. Métricas avançadas (TE/CVaR), stress tests leves.
3. Modo **tempo real** com replay fiel por `run_id`.
4. Ablação e relatório 15–20 págs; scripts de reprodutibilidade.
5. Observabilidade robusta (dashboards Grafana), auditoria detalhada.

---

## 10) Plano B (versão reduzida)

**Objetivo:** provar o conceito com **mínimo atrito**, mantendo a narrativa e a auditabilidade.

* **Pesquisa:** só *Datasets* (preços + 1–2 macro) e *Notícias* básicas (RSS).
* **Forecast:** somente SARIMAX + XGBoost; 3 folds; blend simples (média ponderada).
* **Gênio:** compila Analisada sem ESG/filings completos (apenas menções-chave).
* **Montador:** apenas **MV** com caps; **sem** BL/CVaR.
* **Conselho:** regra simples (1 card por perfil).
* **UI:** vila com 3–4 casas, animação cinemática fixa; painel de logs/arquivos.
* **Escrivão:** PDF curto (5–6 páginas).
  **Meta:** demo estável em 10–15 min por run, artefatos claros, replay ok.

---

## 11) Plano C (versão mínima possível)

**Objetivo:** colocar algo **no ar** rapidamente para mostrar o conceito básico.

* **Entrada:** lista de tickers manual + preset.
* **Pesquisa:** **somente preços** (yfinance/Stooq) — sem notícias/ESG.
* **Forecast:** **ETS** simples (auto) — sem blend/backtesting formal (apenas split holdout).
* **Gênio:** compila **Analisada** minimal (preço, volatilidade, 1 gráfico).
* **Montador:** **Equal‑weight** com caps leves **ou** MV com covariância histórica.
* **Conselho:** botão *Aprovar* (sem loop) com texto gerado.
* **Escrivão:** 2 páginas (carteira + observações).
* **UI:** tela única (sem vila animada), só painel de progresso e resultado.
  **Meta:** apresentar em 1 semana; serve para captar mentor/apadrinhamento.

---

## 12) Checklist operacional (tarefas por trilha)

### Backend

* [ ] Definir Schemas (contracts/) e gerar Pydantic/TS.
* [ ] Modelar BD + migrations Alembic.
* [ ] Implementar ResearchTools (datasets/notícias/relatórios com TTL).
* [ ] Implementar ForecastTools (SARIMAX/ETS/XGB + backtesting).
* [ ] Implementar Gênio (compilador).
* [ ] Implementar BD‑Monitor (completude).
* [ ] Implementar AllocationTools (MV + caps) e ajuste por sentimento.
* [ ] Implementar Conselho (regras).
* [ ] Implementar Escrivão (PDF curto).
* [ ] API gateway + files + WS relay.

### Frontend

* [ ] LeftPanel (presets, auto‑pick/lista, real‑time, Start).
* [ ] VillageStage (mapa, A\*, sprites).
* [ ] RightPanel (Atividades, Arquivos).
* [ ] AgentDock (status).
* [ ] Tema visual (presets).
* [ ] Modo cinemático + replay por run_id.

### Dados & DevOps

* [ ] Registry (empresa↔ticker↔setor).
* [ ] .env e segredos; docker‑compose; dev.sh.
* [ ] Observabilidade (Prometheus/Grafana).
* [ ] CI (lint/test/build); testes E2E com run sintético.
* [ ] Política de licenças/snapshots e retenção.

---

## 13) Riscos & mitigação

* **Fontes instáveis/licença:** priorizar APIs públicas oficiais; manter `access_level`; fallback.
* **Overfitting/performance:** backtesting honesto; blend; limites de tempo por etapa; DM‑test opcional.
* **Demo travar:** modo **cinemático** e artefatos cacheados; vídeo backup.
* **Complexidade:** Plano B/C prontos; esconder avançado por padrão.

---

## 14) Definição de pronto (DoD) por módulo

* **ResearchBundle:** TTL respeitado, snapshots salvos, metadados ok.
* **ForecastResult:** folds concluídos, métrica primária calculada, blend salvo.
* **Ação Analisada:** campos completos, fontes citadas, checksum.
* **PortfolioFinal:** restrições ok, justificativas de ajustes registradas.
* **CouncilDecision:** votos e comentários armazenados.
* **Summary:** PDF/JSON exportado, links válidos, disclaimer presente.
* **UI:** execução fim‑a‑fim reproduzível com `run_id` + replay.

---

## 15) Glossário curto

**Run**: execução completa do pipeline.
**Ação Analisada**: documento padronizado por ticker (insumos + análise + sentimento + risco).
**TTL**: tempo de validade do cache para uma fonte.
**Replay**: reconstrução da animação/logs a partir dos eventos gravados por `run_id`.

