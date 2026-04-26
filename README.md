# ghostprod

**Visibility diagnostics for AI agents on product pages**

*Visible to humans. Invisible to agents.*

![Status](https://img.shields.io/badge/status-active%20research-blue) ![TCC](https://img.shields.io/badge/MBA%20thesis-ICMC%2FUSP-orange) ![Market](https://img.shields.io/badge/market-agentic%20commerce-purple)

---

## The Problem

Product discovery is migrating from search engines to AI agents. ChatGPT, Perplexity, Google AI Mode, and shopping agents are now the first point of contact for millions of purchase decisions. They only recommend what they can read.

Most e-commerce product pages are invisible to agents. Not because the products are bad but because the technical and semantic infrastructure wasn't built for machines.

The evidence:

- **AI Overviews appeared in 14% of shopping queries**, a 5.6× increase in 4 months (BrightEdge, 2025)
- **AI-driven traffic to e-commerce grew 302% in 2025** (Alhena.ai)
- **58% of consumers already use GenAI as a search engine substitute** for product discovery
- **No tool in Brazil specifically measures agent-readiness**

---

## What ghostprod Does

Ghostprod analyzes an e-commerce product page and generates an **Agent-Readiness Score (ARS)**: a number from 0 to 100 indicating whether an AI agent can find, read, and include that product in a comparison or recommendation.

### Score Classification

| Score | Status | What It Means |
|-------|--------|---------------|
| 0–30 | 👻 Ghost | Invisible — critical gaps across all dimensions |
| 31–60 | ⚠️ At Risk | Partially readable — agent includes with incomplete data |
| 61–80 | ✅ Readable | Agent can read and include in comparisons |
| 81–100 | 🟢 Optimized | Agent-ready |

The score integrates three independently measured dimensions: **technical performance** (real Chrome user data via CrUX), **structured markup completeness** (Schema.org), and **content parseability** for machine extraction.

The model considers additional variables beyond the three listed. Complete weights and dimensions are part of the research methodology and will be published with the thesis. (Reach out if you’d like to discuss the remaining variables).

---

## Architecture

```
Input URL
    ↓
┌──────────────────────────────────────────────┐
│            Agent Orchestrator                │
│                                              │
│  Performance     Schema.org      Content     │
│  Field Data      Completeness    NLP         │
│  (CrUX API)      (Playwright)    (spaCy)     │
│                                              │
│              Gap Analysis                    │
│          (Agent Simulator — Gemini API)      │
└──────────────────────────────────────────────┘
    ↓
Agent-Readiness Score (0–100)
+ Breakdown by dimension
+ Recommendations prioritized by impact
```

### Five Specialized Agents

| Agent | Responsibility | Technology |
|-------|---------------|------------|
| **Agent 1 — PageSpeed** | Core Web Vitals (LCP, INP, CLS) via Google PageSpeed Insights API | HTTP REST, API key managed via GCP Secret Manager |
| **Agent 1b — CrUX** | Historical field data from Chrome UX Report | Currently bypassed (score: 0) — intentional design decision: no dashboard for historical tracking yet. Calling the API on every request would waste resources without serving the UI |
| **Agent 2 — Schema** | Renders product page with headless Chrome to read JSON-LD structured data invisible to static crawlers | Playwright with WAF evasion (User-Agent injection to bypass Akamai firewall) |
| **Agent 2.5 — Schema Quality** | Audits the *quality* of structured data — penalizes marketing noise (discounts, superscripts, Black Friday copy) over concrete product attributes | Rule-based scoring |
| **Agent 3 — NLP** | Extracts visible text via headless Chrome and analyzes parseability using NLP engine | Playwright + spaCy |
| **Agent 4 — Gap Analysis** | Compiles all agent outputs into a structured "dossier" assessing agent-readiness | Gemini 1.5 Flash API (migrated from Claude 3.5 for GCP stack standardization) |

### Key Architectural Decisions

**Hybrid Parallelism:** API-only agents (PageSpeed) run in parallel via `ThreadPoolExecutor`. Browser-based agents (Schema, NLP) run sequentially. This resolves a critical deadlock discovered during development: Playwright's `sync_api` is not thread-safe — concurrent browser launches caused bootstrap loops and `ERR_CONNECTION_TIMED_OUT`. The hybrid approach adds ~15 seconds to total request time but guarantees 100% memory stability.

**WAF Evasion:** Akamai's WAF (used by Natura and other major e-commerces) blocks the `HeadlessChrome` User-Agent signature with 403 Forbidden. Solution: inject a standard Windows/Chrome User-Agent in `browser.new_page()`. The Python code now appears as a regular consumer visiting the site.

**CrUX Bypass:** Agent 1b intentionally returns `score: 0`. The decision was made because the frontend doesn't yet have a historical tracking dashboard. Calling the CrUX API on every page load would consume network resources without serving the interface — a product decision, not a technical limitation.

**Model-Agnostic LLM Routing:** Agent 4 (Gap Analysis) was decoupled from a single-provider dependency into a model-agnostic router. It can seamlessly orchestrate different LLMs for comparative scoring — using, for example, **Gemini 1.5 Pro** for deep cloud reasoning, or **Gemma 2.0** via Ollama for high-performance local inference. This architectural choice is a core research feature, allowing the platform to evaluate how different AI "brains" interpret the same e-commerce markup.

---

## Cloud Infrastructure (v0.3)

ghostprod evolved from a local script to a **serverless multi-cloud architecture**:

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | React 19 + Vite 6 + Tailwind CSS 4 | SPA on Firebase Hosting (global CDN) |
| **Backend** | Python 3.11 + FastAPI + Uvicorn | Dockerized on Google Cloud Run (serverless) |
| **Container** | Docker (`mcr.microsoft.com/playwright:v1.40.0-jammy`) | Packages Playwright + Chromium binaries for headless browser in cloud |
| **Secrets** | GCP Secret Manager | API keys (Gemini, PageSpeed) — excluded from Dockerfile |
| **Cost Control** | Cloud Run `--max-instances=2` | Free tier optimization — scales to zero when idle |


## Research Foundation

ghostprod is developed as **applied research** for the MBA in Data Science at ICMC/USP (University of São Paulo).

### Research Question

Can a composite scoring model — based on CrUX field data, structured markup analysis, and NLP content density — reliably predict PDP visibility to AI agents in Brazilian e-commerce? Do the hypothesis-defined weights reflect actual agent behavior when validated empirically?

### Methodology

- **Framework:** CRISP-DM (Cross-Industry Standard Process for Data Mining)
- **Sample:** 10 Brazilian beauty and cosmetics companies across segments — mass market and direct sales (Grupo Boticário, Natura &Co), prestige retail (Sephora Brasil/LVMH, Época Cosméticos/Magazine Luiza), and independent DNVBs (Sallve, Creamy, Principia Skin)
- **Method:** Daily longitudinal collection + controlled simulation experiments with AI agents + supervised model to validate scoring weights
- **Key Finding (in progress):** First score produced — Natura scored 53/100. Same VTEX platform produces opposite Schema.org outcomes: Boticário (CSR implementation) has invisible structured data; Jumbo Chile (SSR implementation) has exemplary Schema. The platform is not the bottleneck — the rendering strategy is.

### Academic Timeline

| Phase | Status | Period |
|-------|--------|--------|
| Market analysis + research design | ✅ Complete | Mar-Apr 2026 |
| Data pipeline (CrUX + Schema + NLP) | 🔄 In Progress | Apr - May 2026 |
| Longitudinal collection, 10 companies | 🔄 In Progress | May - Jun 2026 |
| MVP application | ⏳ Planned | Jun - Jul 2026 |
| Agent simulation experiments | Jul 2026 |
| ML model: learned weights vs. hypothesis | ⏳ Planned | Aug 2026 |
| Thesis submission, ICMC/USP | ⏳ Planned | Jan 2027 |

---

## Competitive Positioning

All 14 commercial GEO/AEO tools identified (Evertune, AthenaHQ, Semrush, Conductor, etc.) measure **output metrics** — citation rates, brand mentions, ranking positions. They answer: *"Are you being cited?"*

ghostprod measures **input metrics** — structural readiness for agent consumption. It answers: *"Can you be read?"*

This is a fundamentally different question. Output metrics tell you the result. Input metrics tell you **why** — and what to fix. This positions ghostprod as a **blue ocean** diagnostic tool: no direct competitor measures agent-readiness at the infrastructure level.

---

## Who This Is For

- **Senior PMs, Heads of Digital, VP E-Commerce** at mid-to-large Brazilian e-commerces who need to justify Schema.org and technical infrastructure investment to CTOs. With data, not intuition.
- **SEO and performance agencies** adding agent-readiness as a new diagnostic service for clients.
- **Platform teams** (VTEX, VNDA, Nuvemshop) evaluating how their rendering choices impact merchants' AI visibility.

---

## Tech Stack

**Frontend (this repository):** React 19 · Vite 6 · Tailwind CSS 4 · Firebase Hosting

**Backend (private repository, active research):** Python 3.11 · FastAPI · Playwright · spaCy · Google Gemini 1.5 Flash · Google CrUX API · BigQuery · Docker · GCP Cloud Run · GCP Secret Manager

---

## Repository Structure

```
ghostprod/ (public)
├── frontend/          ← React application
│   └── src/
│       ├── App.tsx    ← Main UI
│       ├── firebase.ts
│       └── index.css  ← Vaporwave design system
├── docs/              ← Market analysis + methodology
├── README.md
├── CONTRIBUTING.md
└── LICENSE
```

Backend, scoring algorithm, research data, and thesis analysis are maintained in a private repository as part of active academic research. Methodology will be published after thesis submission.

---

## About

**Eva De Paula** — Staff Product Manager with 8 years leading digital products across e-commerce, platform, and B2B operations in Latin America (Brazil, Uruguay, Chile, Argentina + 8 countries).

MBA in Data Science, ICMC/USP (thesis in progress). Researching Agentic Commerce: how AI agents are reshaping product discovery and what e-commerce infrastructure needs to change to remain visible.

ghostprod is simultaneously a **research instrument**, a **functional product**, and a **market hypothesis**. Built end-to-end by a PM directing AI code agents: from data pipeline to frontend to academic methodology.

---

## Links

🌐 [Landing Page](https://britneyscripts.github.io/ghostprod) · 📝 [Substack @britneyscripts](https://britneyscripts.substack.com) · 💼 [LinkedIn](https://linkedin.com/in/evadepaula) · 🎓 [ICMC/USP](https://icmc.usp.br)

---

## License

MIT. See [LICENSE](LICENSE).

---

*Built with Python · FastAPI · React · Playwright · spaCy · Google Gemini API · Google CrUX API · BigQuery · Docker · GCP Cloud Run · Firebase · ICMC/USP*
