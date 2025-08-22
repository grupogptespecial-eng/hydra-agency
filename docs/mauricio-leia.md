# mauricio-leia.md — Guia do Front (Cidade‑IA)

> **Propósito:** orientar a implementação base do front **sem código**, descrevendo primeiro a **lógica de comunicação (quem fala com quem e quando)** e depois as **regras do mundo** (grafo, casas, estados, movimentação, aparência e conexões). Este é o documento de referência para deixar todos alinhados.

---

## PARTE A — Lógica de comunicação (quem fala com quem)

### 1) Visão geral do fluxo

1. **Idealizador/Cliente** envia **códigos de ações** e escolhe um **preset**. O pedido é registrado.
2. **Equipe de Pesquisadores (4 frentes)** checa o **BD**. Se faltar/expirar, coleta dados **em três níveis**: **geral**, **setor**, **empresa**.
3. **Pesquisador de Datasets** produz o **dataset padronizado** e **entrega ao Analista**. Os demais pesquisadores (Relatórios, Notícias, ESG) **entregam ao Gênio**.
4. **Analista** roda a **ferramenta de previsão** sobre o dataset padronizado e **entrega ao Gênio**: previsões, métricas de erro, risco e possível rentabilidade.
5. **Gênio (Compilador)** **não orquestra tarefas**. Ele **compila** tudo que recebeu (insumos semânticos, resultado do Analista, sentimento próprio e o código da ação) e **grava a Ação Analisada** no **BD**.
6. Quando **todas as ações** do pedido estão **compiladas** no BD, o próprio **BD** dispara o **Montador de Carteira**.
7. **Montador** cria a **carteira base** (respeitando risco/caps) e aplica **ajustes pequenos por sentimento** com **justificativa**.
8. **Conselho (C/M/A)** **vota**. Se não aprovar, devolve **diretrizes objetivas** e o processo volta ao **Montador** até aprovar.
9. **Escrivão** gera o **PDF/JSON** final e entrega à **UI**.

### 2) Mapa de comunicação um‑a‑um (função, ferramentas, de quem recebe, para quem entrega)

| Agente                    | O que faz                                                                                                      | Ferramentas que usa                                                          | Recebe de                                               | Entrega para                                         |
| ------------------------- | -------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------- | ------------------------------------------------------- | ---------------------------------------------------- |
| Idealizador/Cliente       | Envia códigos e preset; inicia o run                                                                           | UI (formulário)                                                              | —                                                       | BD                                                   |
| Pesquisador de Relatórios | Coleta relatórios/filings/apresentações nos 3 níveis (geral/setor/empresa), salva snapshots                    | CompanyReportsTool (CVM/SEC/RI), parser de PDF/texto, dedupe                 | BD (pedido, cache/TTL)                                  | Gênio                                                |
| Pesquisador de Notícias   | Coleta notícias (RSS/GDELT), deduplica e atribui sentimento inicial                                            | NewsTool (RSS/Atom, GDELT), simhash, classificação por empresa/setor         | BD (pedido, cache/TTL)                                  | Gênio                                                |
| Pesquisador de ESG        | Coleta relatórios/indicadores ESG, extrai trechos relevantes                                                   | ESGReportsTool (GRI/TCFD), parser de PDF, extrator de métricas               | BD (pedido, cache/TTL)                                  | Gênio                                                |
| Pesquisador de Datasets   | Prepara dataset padronizado (preços + regressoras macro/setoriais/empresa)                                     | DatasetsTool (preços, macro APIs), normalização/qualidade                    | BD (pedido, cache/TTL)                                  | Analista                                             |
| Analista                  | Roda previsão, calcula métricas de erro/risco/retorno por ação                                                 | Forecast Tool (ETS/ARIMA/SARIMAX/UCM, VAR/BVAR, XGB/LGBM; backtesting/blend) | Pesq. de Datasets                                       | Gênio                                                |
| Gênio (Compilador)        | Compila insumos semânticos + resultado do Analista + sentimento próprio + código da ação em **Ação Analisada** | Compiler, Agregador de Sentimento (NLP/NER/sumarização com fontes)           | Relatórios/Notícias/ESG, Analista                       | BD                                                   |
| Banco de Dados (BD)       | Armazena tudo; monitora completude do run e dispara montagem da carteira                                       | Postgres (NOTIFY/LISTEN), MinIO/S3 (artefatos), Redis (cache)                | Gênio, Conselho, Escrivão                               | Montador (quando “todos compilados”); UI (artefatos) |
| Montador de Carteira      | Otimiza carteira base e aplica **ajustes pequenos por sentimento** com justificativa                           | Allocation Tools (MV/Black‑Litterman/Risk Parity/CVaR), Ajuste Sentimental   | BD (Ações Analisadas), Conselho (diretrizes se refazer) | Conselho; BD (carteira final)                        |
| Conselho (C/M/A)          | Vota Aprovar/Refazer com comentários objetivos                                                                 | Rule Engine (limiares por preset)                                            | Montador                                                | BD (decisão); Montador (diretrizes se refazer)       |
| Escrivão (Resumo)         | Gera PDF/JSON final com fontes e narrativa                                                                     | Report Builder (templates)                                                   | BD (carteira aprovada, análises)                        | UI (PDF/JSON)                                        |

### 3) O que aparece na tela quando há comunicação

* Quando alguém **entrega algo** para outro agente/fixture, o personagem **sai de sua casa**, percorre o **caminho do grafo** até a **casa/fixture de destino**, realiza uma **conversa breve** (animação curta) e **retorna à própria casa**.
* Quando alguém **trabalha sozinho**, permanece **na própria casa** com animação de trabalho.
* Sem tarefa, o personagem fica **Dormindo** na própria casa.

> **Importante:** o BD é um **prédio central** na vila (um “servidor”). Ele não “anda”, mas podemos representar entregas **indo até ele** (por exemplo, o **Gênio** levando a Ação Analisada ao prédio do BD).

---

## PARTE B — Regras do mundo (grafo, casas, estados e aparência)

### 4) Grafo principal e casas

* Existe uma **espinha central** (caminho principal) que atravessa a vila.
* **Toda casa é um nódulo** (nó) do grafo, ligada à espinha por um **ramo curto**.
* **Fixtures** (ex.: Praça/Recepção, Quadro de Avisos) também são **nós**.
* **Conexões** são **fixas** (sem paredes/colisões): o personagem **sempre** anda de **nó em nó** pelas **arestas definidas**.
* **Casas obrigatórias** (cada uma com seu nó): Idealizador/Recepção, Relatórios, Notícias, ESG, Datasets, Analista, Gênio, **BD (prédio)**, Montador, Conselho, Escrivão.
* **Sinalização visual**: cada casa tem **placa/ícone** que indica o agente.

### 5) Movimento e caminhos

* **Algoritmo:** para ir de um nó a outro, usar **Dijkstra** (menor caminho nas arestas existentes).
* **Rota:** o personagem **sai da casa de origem → segue pelo grafo → chega ao destino → retorna à própria casa pelo grafo**.
* **Sem atalhos** fora das arestas, **sem atravessar gramado**; o **caminho é visível** e previsível.
* **Ritmo:** velocidade constante; **paradas curtas** na chegada para simular conversa/entrega.

### 6) Estados de cada personagem (o que mostram)

* **Dormindo**: quando não há tarefa. Animação sutil (respirar/piscar) **na própria casa**.
* **Trabalhar Sozinho**: animação de trabalho **na própria casa** (digitar, engrenagem girando, gráficos).
* **Comunicar**:

  1. **Andar** da origem até o destino pelo grafo;
  2. **Conversar/Entregar** (2–3 segundos);
  3. **Voltar** à sua casa pelo grafo;
  4. Terminar em **Dormindo** ou **Trabalhar Sozinho**, conforme a próxima tarefa.

### 7) Aparência e camadas

* **Estilo:** 2D, top‑down leve, vibe **16‑bit** limpa.
* **Camadas:** chão → personagens → árvores/placas (sobreposição “por cima” quando necessário).
* **Câmera:** **zoom** (0.8× a 2.0×) e **pan** por arraste. Foco pode “seguir” um personagem quando o usuário clicar no card dele.
* **Clareza:** caminhos desenhados com **textura própria** (rua/calcário) para reforçar a ideia de **rota fixa**.

### 8) Regras de conexão entre casas

* Toda casa deve estar **conectada à espinha** por **pelo menos uma aresta** curta.
* Casas que trocam muitas mensagens (ex.: **Gênio ↔ BD**, **Montador ↔ Conselho**) devem estar **mais próximas** na topologia para tornar o fluxo **visível e natural**.
* A **Praça/Recepção** (entrada/Idealizador) fica **no início** da espinha; o **BD** fica **no centro**; o **Escrivão** próximo ao **BD** (saída dos relatórios).

### 9) Durações e feedbacks visuais (sugestão)

* **Andar**: tempo proporcional ao comprimento do caminho (constante de velocidade definida).
* **Conversar/Entregar**: **2–3s** com balão/ícone (envelope, gráfico, documento).
* **Trabalhar Sozinho**: ciclos curtos repetidos (ex.: 4–6s).
* **Erros** (quando houver): badge vermelho no card do agente + balão curto “Falhou • Tente novamente”.

---

## PARTE C — Como aplicar isso para **cada agente**

> Abaixo, para cada personagem, **o que faz**, **onde fica** e **com quem se conecta** na cena.

* **Idealizador/Cliente (Recepção)**
  **Faz:** recebe códigos/preset e inicia o run.
  **Casa:** **Praça/Recepção**, no início da espinha.
  **Conecta‑se:** visualmente ao **BD** (entrada do pedido).

* **Pesquisador de Relatórios**
  **Faz:** coleta relatórios/filings/presentations (3 níveis).
  **Casa:** próxima ao início da espinha.
  **Conecta‑se:** **Gênio** (entrega insumos semânticos).

* **Pesquisador de Notícias**
  **Faz:** coleta notícias, deduplica e marca sentimento inicial (3 níveis).
  **Casa:** próxima ao Pesq. de Relatórios.
  **Conecta‑se:** **Gênio**.

* **Pesquisador de ESG**
  **Faz:** coleta indicadores/trechos ESG (3 níveis).
  **Casa:** próxima ao Pesq. de Notícias.
  **Conecta‑se:** **Gênio**.

* **Pesquisador de Datasets**
  **Faz:** prepara dataset padronizado (preços + regressoras) após checar BD/TTL (3 níveis).
  **Casa:** um pouco **acima** na espinha (dá ideia de “dados brutos entrando”).
  **Conecta‑se:** **Analista** (entrega dataset).

* **Analista**
  **Faz:** roda previsão, mede erro/risco/retorno e produz resultados.
  **Casa:** ao **lado** do Pesq. de Datasets.
  **Conecta‑se:** **Gênio** (entrega resultados).

* **Gênio (Compilador)**
  **Faz:** compila insumos semânticos + resultados do Analista + sentimento próprio + código da ação → **Ação Analisada**.
  **Casa:** **antes** do **BD**, na espinha central.
  **Conecta‑se:** **BD** (grava compilado).

* **Banco de Dados (BD)**
  **Faz:** guarda tudo; quando todas as ações do run estão compiladas → **dispara Montador**.
  **Casa:** **prédio central**, no meio da espinha (ícone de servidor).
  **Conecta‑se:** **Montador** (sinal de “pode montar”).

* **Montador de Carteira**
  **Faz:** carteira base + pequenos ajustes por sentimento com justificativa.
  **Casa:** **acima** do BD (dá a sensação de etapa avançada).
  **Conecta‑se:** **Conselho** (submete carteira).

* **Conselho (C/M/A)**
  **Faz:** vota Aprovar/Refazer; se Refazer, devolve diretrizes objetivas.
  **Casa:** topo do mapa (símbolo de tribunal/selo).
  **Conecta‑se:** **Montador** (quando pede refazer) e **Escrivão** (quando aprova).

* **Escrivão (Resumo)**
  **Faz:** PDF/JSON final com fontes; entrega à UI.
  **Casa:** próximo ao **BD**, na saída da espinha (ícone de documento).
  **Conecta‑se:** visualmente à **Praça/Recepção** (representa a entrega ao usuário).

---

## PARTE D — O que é obrigatório na primeira entrega do front base

1. **Grafo visível** com **espinha central** e **casas como nós** ligados por ramos curtos.
2. **Três estados** por personagem: **Dormindo**, **Trabalhar Sozinho**, **Comunicar** (ir → conversar → voltar).
3. **Movimentação sempre pelo grafo** (sem cortar caminho), ida **e** volta após comunicação.
4. **Caminhos previsíveis** (arestas desenhadas com textura própria).
5. **Casas sinalizadas** por ícone/placa (relatórios, notícias, ESG, datasets, analista, gênio, BD, montador, conselho, escrivão).
6. **Câmera** com zoom/pan; foco ao clicar num personagem.
7. **Painel lateral** com duas abas: **Atividades** (narra comunicações e trabalhos) e **Arquivos** (lista de artefatos).
8. **Modo cinemático** opcional (condensa o tempo em ~45–60s), mantendo a ordem dos acontecimentos.

---

## PARTE E — Critérios de clareza para a animação

* O usuário precisa **entender o fluxo só olhando**: quem está trabalhando, quem está indo falar com quem, e o que já foi entregue.
* **Sem jitter/teleporte**: todo deslocamento é **visível** e **motivável** (há um motivo claro para a ida).
* **Justificativas visuais**: quando houver ajuste por sentimento, mostrar um **balão/ícone** que indique a razão (ex.: “notícia negativa” → setinha leve reduzindo peso).

---

## PARTE F — Notas finais

* Este guia **não inclui código** de propósito. Ele é a “bíblia” do comportamento da cidade.
* Se algum fluxo mudar (ex.: inclusão de novo agente/fixture), **atualize aqui primeiro** para manter todo mundo alinhado.
