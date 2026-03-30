# ghostprod

**Diagnóstico de visibilidade para agentes de IA em páginas de produto**

> *Visível para humanos. Invisível para agentes.*

[![Status](https://img.shields.io/badge/status-pesquisa%20em%20andamento-8A2BE2?style=flat-square)](https://britneyscripts.github.io/ghostprod)
[![TCC](https://img.shields.io/badge/TCC-ICMC%2FUSP-FF6B00?style=flat-square)](https://icmc.usp.br)
[![Mercado](https://img.shields.io/badge/mercado-Brasil-009c3b?style=flat-square)](https://britneyscripts.github.io/ghostprod)

---

## O problema

A descoberta de produtos está migrando dos buscadores para agentes de IA. ChatGPT, Perplexity, Google AI Mode e agentes de compra são hoje o primeiro ponto de contato de milhões de decisões de compra — e eles só recomendam produtos que conseguem ler.

A maioria das PDPs do e-commerce brasileiro é invisível para agentes. Não porque os produtos sejam ruins. Porque a infraestrutura técnica e semântica não foi construída para máquinas.

**As evidências:**
- AI Overviews apareceram em 14% das queries de compra — crescimento de **5,6× em 4 meses** (BrightEdge, 2025)
- Tráfego de IA para e-commerces cresceu **302% em 2025** (Alhena.ai)
- **58%** dos consumidores já usam GenAI como substituto do buscador para descoberta de produtos
- **Nenhuma ferramenta** no Brasil mede especificamente agent-readiness

---

## O que o ghostprod faz

O ghostprod analisa uma página de produto de e-commerce e gera um **Agent-Readiness Score (ARS)** — um número de 0 a 100 que indica se um agente de IA consegue encontrar, ler e incluir aquele produto em uma comparação ou recomendação.

**Classificação do score:**

| Score | Status | O que significa |
|-------|--------|-----------------|
| 0–30 | 👻 Ghost | Invisível — gaps críticos em todas as dimensões |
| 31–60 | ⚠️ Em risco | Parcialmente legível — agente inclui com dados incompletos |
| 61–80 | ✅ Legível | Agente consegue ler e incluir na comparação |
| 81–100 | 🟢 Otimizado | Pronto para agentes |

O score é construído sobre três dimensões medidas de forma independente: **performance técnica** (dados reais de usuários Chrome via CrUX), **completude de marcação estruturada** (Schema.org) e **parseabilidade de conteúdo** para extração por máquinas.

---

## Arquitetura

```
URL de entrada
      ↓
┌──────────────────────────────────────────┐
│           Orquestrador de Agentes        │
│                                          │
│  Performance    Schema.org    Conteúdo   │
│  Field Data     Completude    NLP        │
│  (CrUX API)     (Playwright)  (spaCy)    │
│                                          │
│              Gap Analysis                │
│          (Simulador de Agente)           │
└──────────────────────────────────────────┘
      ↓
Agent-Readiness Score (0–100)
+ Breakdown por dimensão
+ Recomendações priorizadas por impacto
```

**Stack frontend** (este repositório):
React 19 · Vite 6 · Tailwind CSS 4 · Firebase Hosting

**Stack backend** (repositório privado — pesquisa ativa):
Python 3.11 · FastAPI · Playwright · spaCy · Google CrUX API · BigQuery

---

## Base de pesquisa

O ghostprod é desenvolvido como pesquisa aplicada para um **MBA em Ciência de Dados no ICMC/USP** (Universidade de São Paulo).

A pesquisa investiga se um modelo de scoring composto — baseado em dados de campo do CrUX, análise de marcação estruturada e densidade de conteúdo via NLP — consegue prever de forma confiável a visibilidade de PDPs do e-commerce brasileiro para agentes de IA, e se os pesos definidos por hipótese refletem o comportamento real dos agentes quando validados empiricamente.

**Amostra de pesquisa:** 10 empresas brasileiras de beleza e cosméticos em diferentes segmentos — de mass market e venda direta (Grupo Boticário, Natura &Co) a varejo de prestígio (Sephora Brasil/LVMH, Época Cosméticos/Magazine Luiza) e DNVBs independentes (Sallve, Creamy, Principia Skin).

**Método:** Coleta longitudinal diária + experimentos controlados de simulação com agentes + modelo supervisionado para validar os pesos do scoring.

*TCC em andamento — ICMC/USP, 2026.*

---

## Status

| Fase | Status | Período |
|------|--------|---------|
| Análise de mercado + design de pesquisa | ✅ Concluído | Fev 2026 |
| Pipeline de dados (CrUX + Schema + NLP) | 🔄 Em andamento | Mar–Abr 2026 |
| Coleta longitudinal — 10 empresas | 🔄 Em andamento | Abr–Jun 2026 |
| Aplicação MVP | 🔄 Em andamento | Abr–Mai 2026 |
| Experimentos de simulação com agentes | ⏳ Planejado | Mai 2026 |
| Modelo ML — pesos aprendidos vs. hipótese | ⏳ Planejado | Jun 2026 |
| Submissão TCC — ICMC/USP | ⏳ Planejado | Jul 2026 |

---

## Para quem é

**PMs Senior, Heads of Digital, VP E-Commerce** de e-commerces brasileiros de médio e grande porte que precisam justificar investimento em Schema.org e infraestrutura técnica para CTOs — com dado, não intuição.

**Agências de SEO e performance** que adicionam agent-readiness como novo serviço de diagnóstico para clientes.

---

## Sobre

**Eva De Paula** — Senior Lead PM com 15+ anos em e-commerce e tech de varejo no Brasil e Uruguai. Retornando ao Brasil em 2026.

MBA em Ciência de Dados — ICMC/USP (TCC em andamento).
Publica pesquisa original sobre agentic commerce no Substack.

O ghostprod é simultaneamente um instrumento de pesquisa, um produto funcional e uma hipótese de mercado — construído de ponta a ponta por uma PM: do pipeline de dados ao frontend até a metodologia acadêmica.

---

## Links

🌐 [Landing page](https://britneyscripts.github.io/ghostprod) &nbsp;·&nbsp;
📝 [Substack @evadepaula](https://substack.com/@evadepaula) &nbsp;·&nbsp;
💼 [LinkedIn](https://linkedin.com/in/eva-de-paula) &nbsp;·&nbsp;
🎓 [ICMC/USP](https://icmc.usp.br)

---

## Estrutura do repositório

```
ghostprod/ (público)
├── frontend/          ← aplicação React
│   └── src/
│       ├── App.tsx    ← UI principal
│       ├── firebase.ts
│       └── index.css  ← design system vaporwave
├── docs/              ← análise de mercado + metodologia
├── README.md
├── CONTRIBUTING.md
└── LICENSE
```

*Backend, algoritmo de scoring, dados de pesquisa e análise do TCC são mantidos em repositório privado como parte da pesquisa acadêmica ativa. A metodologia será publicada após a submissão da tese.*

---

## Licença

MIT — ver [LICENSE](LICENSE)

---

<sub>Construído com Python · FastAPI · React · Playwright · spaCy · Google CrUX API · BigQuery · ICMC/USP</sub>
