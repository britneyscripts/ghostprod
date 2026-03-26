# 👻 ghostprod

**Seu produto existe. Visível para humanos. Invisível para agentes..**

[![Status](https://img.shields.io/badge/status-v0.1%20beta-8A2BE2?style=flat-square)](https://ghostprod.io)
[![License](https://img.shields.io/badge/license-MIT-00CED1?style=flat-square)](LICENSE)
[![Brasil](https://img.shields.io/badge/mercado-Brasil-009c3b?style=flat-square)](https://ghostprod.io)
[![Tese](https://img.shields.io/badge/pesquisa-ICMC%2FUSP-FF6B00?style=flat-square)](https://ghostprod.io)

---

```
  👻  +  🤖  =  ?

  O seu produto está visível
  para os agentes de IA que
  estão redefinindo como as
  pessoas compram online?
```

---

## O que é

**ghostprod** é uma ferramenta de diagnóstico de visibilidade para agentes de IA. Ela analisa uma página de produto (PDP) de e-commerce e retorna um **Agent-Readiness Score (ARS)** de 0 a 100 — indicando se aquela página seria encontrada, lida e incluída em uma comparação por um agente de Level 1.

Desenvolvida como parte de uma pesquisa do MBA em ciência de dados no **ICMC/USP** sobre agentic commerce no Brasil.

---

## Por que isso importa

O tráfego de IA para e-commerces cresceu **302% em 2025**. O ChatGPT gerou mais de **6,1 milhões de visitas** aos 10 maiores e-commerces brasileiros. Os agentes recomendam o que conseguem ler — e a maioria das PDPs brasileiras é invisível para eles.

```
Google Rich Results Tool  →  encontra Schema ✓  (espera JS)
Agente com timeout curto  →  não encontra     ✗  (desiste antes)
ghostprod                 →  mede os dois     ✓  (diz a verdade)
```

---

## Como funciona

O ghostprod roda um **orquestrador de 4 agentes** em paralelo:

```
URL da PDP
    │
    ├── Agente 1: CrUX API
    │   └── LCP, TTFB, INP, CLS (dados de campo reais do Chrome)
    │
    ├── Agente 2: Playwright + Schema Parser
    │   └── JSON-LD completude — espera o JS renderizar
    │
    ├── Agente 3: NLP Scorer (spaCy pt)
    │   └── densidade de atributos técnicos vs marketing gloss
    │
    └── Agente 4: Gap Analysis (Claude API)
        └── simula um agente real: consegue responder
            "sérum para pele oleosa com niacinamida"
            com os dados disponíveis nessa PDP?
            │
            └── se não → identifica qual campo está faltando

Agent-Readiness Score = (Perf × 0.40) + (Schema × 0.40) + (NLP × 0.20)
```

### Classificação do score

| Score | Classificação | Significado |
|-------|--------------|-------------|
| 0–30 | 👻 **Fantasma** | Invisível — problemas críticos nas 3 variáveis |
| 31–60 | ⚠️ **Em risco** | Parcialmente legível — agente inclui com dados incompletos |
| 61–80 | ✅ **Legível** | Agente consegue parsear e incluir na comparação |
| 81–100 | 🏆 **Otimizado** | Agent-ready — Pacman come o ghost |

---

## Stack técnica

### Frontend (AI Studio → GitHub)
```
React + Tailwind CSS
Identidade vaporwave: #0F0F2A / #00CED1 / #8A2BE2 / #FF00FF
Orbitron (score) · Inter (body) · Roboto Mono (dados técnicos)
Firebase Hosting
```

### Backend (produção)
```
Python 3.11 + FastAPI
Playwright (headless Chromium) — renderiza JS antes de parsear
BeautifulSoup — extrai JSON-LD estruturado
spaCy pt_core_news_sm — NLP scorer
CrUX API — dados reais de campo do Google
Google Cloud Run (southamerica-east1) — free tier
```

### Dados
```
Firebase Firestore — rate limiting + captura de leads beta
Sem banco de dados persistente na v0.1 — resultados em sessão
```

---

## Estrutura do repositório

```
ghostprod/
├── README.md
├── CONTRIBUTING.md
├── docs/
│   ├── architecture.md        ← diagrama de arquitetura
│   ├── api.md                 ← endpoints FastAPI
│   ├── score-calculation.md   ← como o ARS é calculado
│   └── lgpd.md                ← política de privacidade técnica
│
├── frontend/                  ← React (origem: AI Studio)
│   ├── src/
│   │   ├── App.tsx            ← UI principal vaporwave
│   │   ├── firebase.ts        ← conexão Firestore
│   │   └── index.css          ← design system
│   ├── firestore.rules        ← regras default deny
│   └── package.json
│
├── backend/                   ← Python (origem: scanner.py)
│   ├── main.py                ← FastAPI app + endpoints
│   ├── scanner.py             ← pipeline principal
│   ├── agents/
│   │   ├── agent1_crux.py     ← CrUX API → Performance Score
│   │   ├── agent2_schema.py   ← Playwright → Schema Score
│   │   ├── agent3_nlp.py      ← spaCy → Conteúdo Score
│   │   └── agent4_gap.py      ← Claude API → Gap Analysis
│   ├── orchestrator.py        ← coordena os 4 agentes
│   └── tests/
│       └── test_scanner.py
│
└── .github/
    └── workflows/
        ├── ci.yml             ← testes automáticos
        └── deploy.yml         ← deploy para Cloud Run
```

---

## Rodando localmente

### Pré-requisitos
- Python 3.11+
- Node.js 18+
- Docker (para Cloud Run local)
- Conta Google Cloud (free tier suficiente)

### Backend

```bash
# Clone o repositório
git clone https://github.com/ghostprod-io/ghostprod.git
cd ghostprod/backend

# Instala dependências
pip install -r requirements.txt

# Instala Playwright
playwright install chromium

# Instala modelo spaCy PT
python -m spacy download pt_core_news_sm

# Copia e configura variáveis de ambiente
cp .env.example .env
# edite .env com suas chaves

# Roda o servidor
uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd ghostprod/frontend

# Instala dependências
npm install

# Copia e configura Firebase
cp .env.example .env.local
# edite com suas credenciais Firebase

# Roda em desenvolvimento
npm run dev
```

### Variáveis de ambiente

```env
# backend/.env
ANTHROPIC_API_KEY=sk-ant-...          # Claude API (Agente 4)
CRUX_API_KEY=...                       # opcional — CrUX tem quota sem chave
RATE_LIMIT_PER_IP=10                   # análises por IP por dia
RATE_LIMIT_MONTHLY=500                 # total mensal
ALLOWED_ORIGINS=http://localhost:3000  # CORS

# frontend/.env.local
VITE_FIREBASE_API_KEY=...
VITE_FIREBASE_AUTH_DOMAIN=...
VITE_FIREBASE_PROJECT_ID=...
VITE_API_URL=http://localhost:8000
```

---

## Rodando os testes

```bash
cd backend

# Testes unitários
pytest tests/ -v

# Testes com cobertura
pytest tests/ --cov=. --cov-report=term-missing

# Teste específico do scanner
pytest tests/test_scanner.py -v -k "test_schema"
```

---

## O que o AI Studio gerou e o que mudamos

O ghostprod começou como protótipo no Google AI Studio. Aqui está o que aproveitamos e o que substituímos:

| Componente | AI Studio (origem) | Produção (este repo) | Por quê |
|---|---|---|---|
| UI React + design vaporwave | ✅ mantido | ✅ mantido | Funciona — não refaz |
| Firebase Firestore (leads) | ✅ mantido | ✅ mantido | Free tier generoso |
| Express proxy (backend) | ❌ descartado | FastAPI + Playwright | Express não renderiza JS — Schema CSR = sempre zero |
| CrUX simulado | ❌ descartado | CrUX API real | Dado falso não serve para tese |
| Gemini no frontend | ❌ descartado | Claude API no servidor | API key exposta no browser = risco de segurança |

---

## Limitações da v0.1

- **500 análises/mês** (hard limit — controle de custo pré-monetização)
- **10 análises/dia por IP**
- **Desktop only** — sem versão mobile
- **Brasil only** — CrUX e NLP calibrados para PT-BR
- **Pesos hipótese** (40/40/20) — serão validados empiricamente pela pesquisa ICMC/USP

---

## Regras do repositório

```
🚫 PROIBIDO deploy às sextas-feiras
   Freeze: sexta 11h → segunda 9h

Branches:
  main      → produção (protegida — PR obrigatório)
  develop   → staging (todo deploy vai aqui primeiro)
  feature/* → novas features
  hotfix/*  → correções urgentes → merge em main E develop
```

---

## Conformidade LGPD

O ghostprod é exclusivo para o mercado brasileiro e segue a Lei Geral de Proteção de Dados (Lei 13.709/2018).

- **Dados coletados:** URL analisada (pública), e-mail (voluntário), IP (rate limiting)
- **Não coletamos:** dados sensíveis, perfil de usuário, histórico de navegação
- **Retenção:** IP por 30 dias · e-mail até descadastro · URLs não armazenadas
- **Servidor:** Cloud Run em `southamerica-east1` (São Paulo)
- **Política completa:** [ghostprod.io/privacidade](https://ghostprod.io/privacidade)

---

## Pesquisa acadêmica

Este projeto é parte da tese de MBA em Ciência de Dados do **ICMC/USP** sobre agentic commerce no Brasil.

**Hipótese da tese:** as três variáveis (performance técnica, completude de Schema.org e parseabilidade de conteúdo) têm pesos diferentes na predição de invisibilidade semântica para agentes de Level 1. O ghostprod é o instrumento de coleta de dados.

**Série Substack:** [Agentic Commerce](https://substack.com/@evadepaula) — artigos sobre como agentes de IA leem (ou não leem) o e-commerce brasileiro.

---

## Autora

**Eva Bettina**
Senior PM · Orquestradora · Curiosa 🔮
MBA Ciência de Dados — ICMC/USP

[LinkedIn](https://linkedin.com/in/eva-de-paula) · [Substack](https://substack.com/@evadepaula) · [ghostprod.io](https://ghostprod.io)

---

## Feito com carinho por 💜

```
Eva Bettina          🧠  Senior PM · Orquestradora · Curiosa
Claude (Anthropic)   🤍  Arquitetura · Código · Documentação
Gemini (Google)      💙  Gap Analysis · UI Prototyping
AI Studio (Google)   🩵  Frontend vaporwave
Opal (Google Labs)   💜  Prototipagem visual   
```

> *"A melhor stack é a que resolve o problema — com ou sem framework."*

---

## Licença

MIT — veja [LICENSE](LICENSE)

---

```
[ SYSTEM STATUS: v0.1 BETA // SIGNAL: BUILDING ]

  👻  Se você chegou até aqui,
      o ghostprod conseguiu te parsear.
```
