# ghostprod

**AI Visibility Diagnostic for E-Commerce Product Pages**

> *Visível para humanos. Invisível para agentes.*

[![Status](https://img.shields.io/badge/status-research%20in%20progress-8A2BE2?style=flat-square)](https://britneyscripts.github.io/ghostprod)
[![Research](https://img.shields.io/badge/TCC-ICMC%2FUSP-FF6B00?style=flat-square)](https://icmc.usp.br)
[![Market](https://img.shields.io/badge/market-Brasil-009c3b?style=flat-square)](https://britneyscripts.github.io/ghostprod)

---

## The Problem

Product discovery is migrating from search engines to AI agents. ChatGPT, Perplexity, Google AI Mode, and shopping agents are now the first touchpoint for millions of purchase decisions — and they can only recommend products they can actually read.

Most Brazilian e-commerce PDPs are invisible to agents. Not because the products are bad. Because the technical and semantic infrastructure wasn't built for machines.

**The evidence:**
- AI Overviews appeared in 14% of shopping queries — grew **5.6× in 4 months** (BrightEdge, 2025)
- AI-driven traffic to e-commerces grew **302% in 2025** (Alhena.ai)
- **58%** of consumers already use GenAI as a substitute for product search
- **No existing tool** in Brazil measures agent-readiness specifically

---

## What ghostprod does

ghostprod analyzes an e-commerce product page and generates an **Agent-Readiness Score (ARS)** — a single number from 0 to 100 indicating whether an AI agent can find, read, and include that product in a comparison or recommendation.

**Score classification:**

| Score | Status | What it means |
|-------|--------|---------------|
| 0–30 | 👻 Ghost | Invisible — critical gaps across all dimensions |
| 31–60 | ⚠️ At Risk | Partially readable — agent includes with incomplete data |
| 61–80 | ✅ Readable | Agent can parse and include in comparison |
| 81–100 | 🟢 Optimized | Agent-ready |

The score is built on three independently measured dimensions: **technical performance** (real field data from Chrome users), **structured markup completeness**, and **content parseability for machine extraction**.

---

## Architecture

```
User URL input
      ↓
┌─────────────────────────────────────────┐
│           Agent Orchestrator            │
│                                         │
│  Performance    Schema.org    Content   │
│  Field Data     Completeness  Parsing   │
│  (CrUX API)     (Playwright)  (NLP)     │
│                                         │
│              Gap Analysis               │
│           (Agent Simulator)             │
└─────────────────────────────────────────┘
      ↓
Agent-Readiness Score (0–100)
+ Dimension breakdown
+ Prioritized recommendations
```

**Frontend stack** (this repository):
React 19 · Vite 6 · Tailwind CSS 4 · Firebase Hosting

**Backend stack** (private repository — active research):
Python 3.11 · FastAPI · Playwright · spaCy · Google CrUX API · BigQuery

---

## Research basis

ghostprod is developed as applied research for an **MBA in Data Science at ICMC/USP** (Universidade de São Paulo).

The research investigates whether a composite scoring model based on CrUX field data, structured markup analysis, and NLP-based content density can reliably predict AI agent visibility for Brazilian e-commerce product pages — and whether hypothesis-defined weights reflect actual agent behavior when validated empirically.

**Research sample:** 10 Brazilian beauty and cosmetics companies across market segments — from mass market and direct sales (Grupo Boticário, Natura &Co) to prestige retail (Sephora Brasil/LVMH, Época Cosméticos/Magazine Luiza) and independent DNVBs (Sallve, Creamy, Principia Skin).

**Method:** Longitudinal daily data collection + controlled agent simulation experiments + supervised learning model to validate scoring weights.

*Thesis in progress — ICMC/USP, 2026.*

---

## Status

| Phase | Status | Period |
|-------|--------|--------|
| Market analysis + research design | ✅ Complete | Feb 2026 |
| Data pipeline (CrUX + Schema + NLP) | 🔄 In progress | Mar–Apr 2026 |
| Longitudinal collection — 10 companies | 🔄 In progress | Apr–Jun 2026 |
| MVP application | 🔄 In progress | Apr–May 2026 |
| Agent simulation experiments | ⏳ Planned | May 2026 |
| ML model — learned vs. hypothesis weights | ⏳ Planned | Jun 2026 |
| TCC submission — ICMC/USP | ⏳ Planned | Jul 2026 |

---

## Who this is for

**Senior PMs, Heads of Digital, VP E-Commerce** at mid-to-large Brazilian e-commerces who need to justify Schema.org and technical infrastructure investment to CTOs — with data, not intuition.

**SEO and performance agencies** adding agent-readiness as a new diagnostic offering for clients.

---

## About

**Eva De Paula** — Senior Lead PM with 15+ years in e-commerce and retail tech across Brazil and Uruguay. Returning to Brazil in 2026.

MBA in Data Science — ICMC/USP (thesis in progress).
Publishes original research on agentic commerce at Substack.

ghostprod is simultaneously a research instrument, a working product, and a market hypothesis — built end-to-end by one PM, from data pipeline to frontend to academic methodology.

---

## Links

🌐 [Landing page](https://britneyscripts.github.io/ghostprod) &nbsp;·&nbsp;
📝 [Substack @evadepaula](https://substack.com/@evadepaula) &nbsp;·&nbsp;
💼 [LinkedIn](https://linkedin.com/in/eva-de-paula) &nbsp;·&nbsp;
🎓 [ICMC/USP](https://icmc.usp.br)

---

## Repository structure

```
ghostprod/ (public)
├── frontend/          ← React application
│   └── src/
│       ├── App.tsx    ← main UI
│       ├── firebase.ts
│       └── index.css  ← vaporwave design system
├── docs/              ← market analysis + methodology (in progress)
├── README.md
├── CONTRIBUTING.md
└── LICENSE
```

*Backend, scoring algorithm, research data and TCC analysis are maintained in a private repository as part of active academic research. Methodology will be published upon thesis submission.*

---

## License

MIT — see [LICENSE](LICENSE)

---

<sub>Built with Python · FastAPI · React · Playwright · spaCy · Google CrUX API · BigQuery · ICMC/USP</sub>
