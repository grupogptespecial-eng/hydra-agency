# Hermes — README (Mega)

> **Tagline:** IA que **explica** finanças, não só prevê. Uma cidade viva onde cada agente mostra, passo a passo, como uma carteira nasce.

---

## 📌 Cinco passos (pedido do autor)

**ENTENDER** — Construir um sistema que recebe **códigos de ações**, coleta/normaliza dados em **3 níveis** (geral, setor, empresa), gera **previsões e métricas**, compila tudo em **Ações Analisadas**, monta/ajusta uma **carteira** sob restrições de risco, submete a um **Conselho** e entrega um **PDF** explicável — com uma **UI gamificada** (Cidade‑IA).

**ANALISAR** — Componentes: Idealizador (UI), Pesquisadores (Relatórios/Notícias/ESG/Datasets), Analista (Forecast), **Gênio (Compilador)**, **Banco de Dados (hub/monitor)**, Montador, Conselho, Escrivão; ferramentas: Pesquisa, Forecast, Alocação, Métricas, NLP, Report; infra: API, storage, logs, CI/CD.

**RACIOCINAR** — Monorepo modular: **apps** (executáveis) vs **packages** (bibliotecas). Contratos únicos (JSON Schema) geram **tipos TS** e **Pydantic**. **BD** emite eventos/NOTIFY e dispara o Montador quando tudo está **compilado**. **Gênio não orquestra** — só compila. UI consome eventos e artefatos.

**SINTETIZAR** — Fluxo dirigido por **completude** no BD. Observabilidade com **logs por run_id** e artefatos versionados. UI exibe **Atividades** (logs) e **Arquivos** (artefatos) e anima a **Vila** por um grafo central.

**CONCLUIR** — Este README descreve visão, arquitetura, contratos, estrutura de pastas, setup, fluxos, UX, cronograma e **Planos B/C** para garantir entrega.

---

## 🧭 Visão

Hermes é uma plataforma **educacional e explicável** de IA Quant. O usuário escolhe um perfil (Conservador/Moderado/Arrojado/Avançado) e fornece tickers (auto‑pick ou lista). A **Cidade‑IA** mostra agentes coletando dados, prevendo, combinando, otimizando e justificando decisões. O resultado é uma **carteira** com relatório **auditável** e **reproduzível**.

**Diferenciais:**

* **Gênio como compilador** (não orquestrador) → simplicidade operacional.
* **BD como hub** (completude → dispara montagem da carteira).
* **Trilha de auditoria visual** (eventos → animações → artefatos com fontes/snapshots).

---

## 🗺️ Fluxo ponta‑a‑ponta

1. **Idealizador/Cliente** envia `tickers[]` + preset.
2. **Pesquisadores (4 frentes)** checam BD/TTL e coletam **geral/setor/empresa**:
   * Relatórios (RI/filings) → **Gênio**
   * Notícias → **Gênio**
   * ESG → **Gênio**
   * **Datasets** (macro/setorial/empresa + preços) → **Analista**
3. **Analista** roda **Forecast Tool** (modelos, backtesting, métricas) e devolve para o **Gênio**.
4. **Gênio (Compilador)** agrega insumos + **sentimento próprio** + **código do ticker** e grava uma **Ação Analisada**.
5. **BD (Monitor)**: quando **todas** as ações do run estiverem **compiladas**, cria **PortfolioBuildRequest**.
6. **Montador** otimiza a **carteira base** (MV/BL/RP/CVaR) e aplica **ajustes pequenos por sentimento** (justificados).
7. **Conselho (C/M/A)** vota; se **Refazer**, volta ao Montador com diretrizes; se **Aprovar**, segue.
8. **Escrivão** gera **PDF/JSON** final.
9. **UI** exibe animações/logs e links para artefatos.

**Tempo real (opcional):** novo dado material reabre partes do ciclo para atualizar carteira e relatório.

---

## 👥 Agentes (função, ferramentas, I/O)

| Agente                  | O que faz                                                   | Ferramentas                                                                  | Recebe de                            | Entrega para                             |
| ----------------------- | ----------------------------------------------------------- | ---------------------------------------------------------------------------- | ------------------------------------ | ---------------------------------------- |
| **Idealizador/Cliente** | Envia tickers/preset (inicia run)                           | UI (form)                                                                    | —                                    | BD                                       |
| **Pesq. Relatórios**    | Coleta RI/filings/apresentações (3 níveis) e salva snapshot | CompanyReportsTool (CVM/SEC/RI), parser PDF/texto                            | BD (pedido, cache/TTL)               | Gênio                                    |
| **Pesq. Notícias**      | Coleta notícias (RSS/GDELT), deduplica, sentimento inicial  | NewsTool (RSS/Atom, GDELT), simhash                                          | BD                                   | Gênio                                    |
| **Pesq. ESG**           | Coleta relatórios/indicadores ESG, extrai trechos           | ESGReportsTool (GRI/TCFD), parser                                            | BD                                   | Gênio                                    |
| **Pesq. Datasets**      | Padroniza datasets (macro/setorial/empresa + preços)        | DatasetsTool, validação/normalização                                         | BD                                   | Analista                                 |
| **Analista**            | Forecast + métricas de erro/risco/retorno                   | Forecast Tool (ETS/ARIMA/SARIMAX/UCM, VAR/BVAR, XGB/LGBM; backtesting/blend) | Pesq. Datasets                       | Gênio                                    |
| **Gênio (Compilador)**  | Compila insumos + sentimento + código → **Ação Analisada**  | Compiler + NLP (NER/sentimento/sumário com fontes)                           | Pesqs., Analista                     | BD                                       |
| **BD (Monitor)**        | Armazena/observa completude do run                          | Postgres/MinIO/Redis                                                         | Gênio, Conselho, Escrivão            | Montador (quando “todos compilados”); UI |
| **Montador**            | Carteira base + ajuste por sentimento (justificado)         | Allocation Tools (MV/BL/RP/CVaR)                                             | BD; Conselho (requisitos se refazer) | Conselho; BD                             |
| **Conselho (C/M/A)**    | Vota, aprova/refaz com comentários objetivos                | Rule Engine                                                                  | Montador                             | BD (decisão); Montador                   |
| **Escrivão**            | Gera PDF/JSON final com fontes                              | Report Builder                                                               | BD                                   | UI                                       |

---

## 🧩 Ferramentas principais

* **Pesquisa** — fontes oficiais + TTL/cache; snapshots obrigatórios.
* **Forecast** — modelos clássicos + ML; backtesting time‑split (5 folds, passo 3m); métrica **sMAPE**; **blend Top‑K**; DM‑test opcional.
* **Alocação** — MV, Risk Parity, Black‑Litterman, CVaR; caps por ativo/setor; metas por preset.
* **Métricas** — Sharpe/Sortino/MaxDD/TE/IR; séries rolling.
* **NLP** — sentimento/NER/sumarização com citações.
* **Report** — PDF curto (pré) e 15–20 págs (final) com ablação.

**APIs prioritárias:** Preços (B3 | yfinance/Stooq), Filings (CVM/RI | SEC EDGAR), Macro (BCB/SGS, IBGE | FRED, World Bank), Notícias (RSS/GDELT), ESG (páginas de Sustentabilidade/RI). Metadados: `license`, `access_level`, `source_url`, `snapshot`.

---

## 🧱 Arquitetura (alto nível)

* **Monorepo**: `apps/` (UI, API, workers), `packages/` (libs), `data/` (artefatos/logs), `assets/`, `configs/`, `scripts/`, `docs/`, `tests/`.
* **API (FastAPI)**: gateway (start run, servir artefatos), relay de eventos do BD via WS.
* **Workers**: pesquisa×4, analista, gênio (compilar), bd‑monitor (completude), portfolio, conselho, escrivão.
* **Storage**: Postgres (metadados), MinIO/S3 (blobs), Redis (cache/TTL). Logs JSONL por `run_id`.
* **UI (React+Pixi)**: vila (grafo central; Dijkstra), Painéis (Atividades/Arquivos), Dock por agente, modos tempo real/cinemático.

## 🧾 Formato de saída (JSON-first)

* **Padrão**: todo agente, ferramenta e serviço deve retornar **JSON válido** conforme os contratos em `packages/contracts/jsonschemas`.
* **Conversão**: respostas externas em XML/CSV devem ser convertidas para JSON antes de qualquer uso interno.
* **Artefatos binários** (PDFs, imagens, Parquet etc.) são salvos como arquivos separados em `data/artifacts/{run_id}/...` e referenciados por um **manifesto JSON** com `path`, `checksum`, `content_type`, `license` e `source_url`.
* **Integração**: a UI e demais serviços consomem sempre JSON; links para arquivos binários partem desses manifestos.

---

## 🗂️ Estrutura de pastas (resumo)

```
projeto-hermes/
├─ apps/
│  ├─ ui-vila/            # frontend (React+Pixi)
│  ├─ api/                # FastAPI gateway
│  ├─ worker-pesquisa/    # relatórios, notícias, esg, datasets
│  ├─ worker-analista/    # forecast & métricas
│  ├─ worker-genio/       # compila Ação Analisada
│  ├─ worker-bd-monitor/  # completude → portfolio
│  ├─ worker-portfolio/   # alocação + ajuste por sentimento
│  ├─ worker-conselho/    # votos C/M/A
│  └─ worker-escrivao/    # PDF/JSON final
├─ packages/
│  ├─ contracts/          # JSON Schemas → TS/Pydantic
│  ├─ research-tools/     # coleta/TTL/snapshots
│  ├─ forecast-tools/     # modelos + backtesting/blend
│  ├─ allocation-tools/   # MV/BL/RP/CVaR
│  ├─ metrics/            # risco/retorno
│  ├─ feature-store/      # features ponto‑no‑tempo
│  ├─ report-builder/     # templates PDF
│  ├─ nlp/                # sentimento/NER/sumário
│  ├─ py-utils/           # db/storage/cache/logs
│  └─ js-utils/           # api/ws/formatters
├─ data/
│  ├─ registry/ raw/ external/ interim/ processed/
│  ├─ artifacts/{run_id}/(research|forecast|portfolio|report)
│  └─ logs/{run_id}.jsonl
├─ assets/  configs/  scripts/  docs/  tests/
└─ README.md
```

---

## 🔐 Contratos & artefatos (fonte da verdade)

* `analysis_request.schema.json` — `{run_id, tickers[], preset, options}`
* `research_bundle.schema.json` — relatórios/notícias/ESG por ticker (metadados com licença/snapshot)
* `dataset.schema.json` — preços/regressoras padronizados (coverage, freq, checksum)
* `forecast_result.schema.json` — leaderboard, blend, métricas, paths
* `acao_analisada.schema.json` — fundamentals{}, esg{}, forecast{}, sentiment{}, risks{}, insights[]
* `portfolio_build_request.schema.json` — objetivo, limites, caps
* `portfolio_draft.schema.json` — weights0{}, metrics{}, exposições{}
* `portfolio_final.schema.json` — weights{}, ajustes_sentimento[], justificativas[]
* `council_decision.schema.json` — votes[], status, comments[]
* `summary.schema.json` — pdf_path, json_path, toc, sources

**Regra**: Schemas geram **Pydantic** (Py) e **tipos TS** (UI). Artefatos vão para `data/artifacts/{run_id}/...`.

---

## ⚙️ Setup rápido

**Pré‑requisitos:** Docker + Docker Compose, Python 3.11, Node 20.

```bash
# 1) clonar e configurar
cp configs/env/.env.example .env
# edite `.env` e preencha FRED_API_KEY, ALPHAVANTAGE_KEY, WIKIRATE_TOKEN etc.

# 2) subir stack local
make dev           # ou scripts/dev.sh

# 3) semear dados de exemplo
python scripts/seed.py

# 4) rodar demo sintética
python scripts/run_demo.py   # emite eventos para a UI
```

**Ambiente:** Postgres (db), Redis (cache), MinIO (blobs), API, um worker de cada tipo, UI.

### Segredos de API

Algumas ferramentas de pesquisa dependem de chaves específicas e já incluem os parâmetros ou cabeçalhos recomendados pelos provedores. Configure as seguintes variáveis de ambiente (ou secrets) antes de executar:

- `ALPHAVANTAGE_KEY` – chave da API Alpha Vantage.
- `FRED_API_KEY` – chave da API FRED.
- `WIKIRATE_TOKEN` – token de acesso ao WikiRate.
- `OPEN_ROUTER_KEY` – chave da API OpenRouter.
- `GOOGLE_IA_STUDIO_API` – chave da API Google AI Studio.
- `SEC_EDGAR_API` – cabeçalhos obrigatórios para chamadas ao SEC EDGAR.

Defina essas chaves no arquivo `.env` antes de rodar o projeto e nunca as versionar no repositório.

### Deploy da UI no GitHub Pages

O repositório inclui um workflow (`.github/workflows/pages.yml`) que compila a pasta `apps/ui-vila` e publica os arquivos estáticos em **GitHub Pages** sempre que a branch `main` recebe novos commits.

Para gerar o build manualmente:

```bash
npm --prefix apps/ui-vila run build
```

O Vite já define `base: '/hydra-agency/'` na etapa de build, garantindo que os assets funcionem sob `https://<usuario>.github.io/hydra-agency/`.


---

## 🧪 Testes

* **Unitários** por pacote (research/forecast/allocation/nlp/metrics).
* **Contract tests** validam JSON contra os Schemas.
* **E2E** com 2–3 tickers: verifica estados no BD e artefatos (research→summary).

---

## 🔭 Observabilidade & qualidade

* **Logs** estruturados (`data/logs/{run_id}.jsonl`) c/ `service`, `stage`, `artifact_path`.
* **Métricas** Prometheus: duração por etapa, erros/100 runs, cache hit‑rate.
* **DQ**: detecção de gaps/splits, staleness, dedupe (sha256 + simhash), *point‑in‑time*.
* **Erros**: taxonomia `E.NET.*`, `E.HTTP.*`, `E.PARSE.*`, `E.MODEL.*`, `E.DATA.*`, `E.LICENSE.*`.

---

## 🖥️ UX (Cidade‑IA)

* **Layout**: esquerda (controles), centro (Vila; grafo central com casas como nós), direita (Atividades/Arquivos), rodapé (Agent Dock).
* **Movimento**: sempre por nós; **Dijkstra**; sem colisão. Estados: **Dormir**, **Trabalhar**, **Comunicar** (ir‑falar‑voltar).
* **Modos**: **tempo real** (pode engasgar) ou **cinemático** (45–60s com a mesma ordem de eventos).
* **Presets**: alteram aparência (manhã/entardecer/neon) e limites de risco.

---

## 📅 Cronograma (MVP → Completo)

**Fase 1 — MVP (4–6 semanas)**

1. Contracts prontos (Schemas → TS/Pydantic)
2. API gateway (start run, WS relay, files)
3. Pesquisa (datasets + notícias/relatórios com TTL)
4. Analista/Forecast (SARIMAX/ETS/XGB; backtesting + blend)
5. Gênio (Compilador)
6. BD‑Monitor + Montador (MV + caps) + Ajuste Sentimental (±1 pp)
7. Conselho (regras simples) + Escrivão (PDF curto)
8. UI vila (cinemático) + Atividades/Arquivos
   **DoD:** run reprodutível fim‑a‑fim com 2–3 tickers.

**Fase 2 — Completo (6–10 semanas)**

* VAR/BVAR, Black‑Litterman, CVaR, ESG parser estruturado
* Métricas avançadas (TE/CVaR), stress tests leves
* Modo **tempo real** + replay fiel; ablação e relatório 15–20 págs
* Observabilidade robusta (dashboards) e auditoria detalhada

---

## 🧭 Planos de contingência

**Plano B (reduzido)**

* Pesquisa: Datasets + Notícias básicas (RSS)
* Forecast: SARIMAX + XGB; 3 folds; **blend simples**
* Gênio: compila sem ESG/filings completos
* Montador: apenas MV + caps
* Conselho: regra simples
* UI: vila com 3–4 casas; cinemático
* Escrivão: PDF 5–6 págs
  **Meta:** demo estável em ~15 min por run.

**Plano C (mínimo possível)**

* Entrada: tickers manuais + preset
* Pesquisa: **somente preços** (yfinance/Stooq)
* Forecast: **ETS** (holdout simples)
* Gênio: Analisada minimal (preço/vol/1 gráfico)
* Montador: Equal‑weight com caps leves (ou MV histórica)
* Conselho: botão Aprovar (sem loop)
* Escrivão: 2 páginas
* UI: tela única sem vila
  **Meta:** apresentar em ~1 semana.

---

## 🧩 Presets de risco (contrato público)

* **Conservador**: Vol ≤ 8%, MaxDD ≤ 15%
* **Moderado**: Vol ≤ 15%, MaxDD ≤ 30%
* **Arrojado**: Vol ≤ 25%, MaxDD ≤ 50%
* **Avançado**: usuário edita TE/CVaR, composição do Conselho e modelos.

---

## ⚖️ Compliance & avisos

* **Metadados obrigatórios**: `license`, `access_level`, `source_url`, `snapshot` para todo documento externo.
* **Retenção**: artefatos/logs por 90 dias (MVP); revisitar na Fase 2.
* **Disclaimer** (app e PDFs): *"Material educativo; não constitui recomendação. Resultados passados não garantem retornos futuros."*

---

## 🤝 Contribuição

1. Crie uma branch a partir de `main`.
2. Rode `make test` antes do PR.
3. PR com descrição, screenshots e links para artefatos (`artifacts/{run_id}`).

**Padrões:** Black/Ruff (Py), ESLint/Prettier (JS), Conventional Commits.

---

## 📚 Licença

Definir (MIT/Apache‑2.0/Proprietária). Arquivo `LICENSE` será adicionado quando escolhido.

---

## 📖 Glossário

**Run** — execução do pipeline.
**Ação Analisada** — documento padronizado por ticker.
**TTL** — tempo de validade do cache.
**Replay** — reencenação da execução a partir dos eventos gravados.
**C/M/A** — Conservador/Moderado/Arrojado (perfis do Conselho).

---

## 📎 Anexos úteis

* `docs/architecture.md` — diagrama macro (mermaid) e fluxos.
* `docs/data-sources.md` — lista detalhada de fontes e TTLs.
* `docs/mauricio-leia.md` — guia do front base (Cidade‑IA).
* `Mapping.md` — plano mestre (tarefas, riscos, DoD, Planos B/C).

