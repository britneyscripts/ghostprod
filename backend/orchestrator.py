"""
ghostprod — orchestrator.py
─────────────────────────────────────────────────────────
Orquestrador: coordena os 4 agentes e calcula o ARS.

NOVO v0.2: Agente 2.5 — Schema Quality Scorer
  - Avalia QUALIDADE do conteúdo do Schema (não só estrutura)
  - Penaliza marketing gloss e campos vazios
  - Retorna 2 scores: structure (existe?) e quality (útil?)

Pesos (hipótese v0.1 — validar com dados da tese):
  Agente 1 — Performance (CrUX):  40%
  Agente 2 — Schema.org:          40%  ← Agora usa quality_score
  Agente 3 — Conteúdo (NLP):      20%

O Agente 4 (Gap Analysis) não entra no score matemático
mas gera o diagnóstico qualitativo e as recomendações.
"""

import concurrent.futures
from agents import agent1_crux, agent1_pagespeed, agent2_schema, agent2_5_schema_quality, agent3_nlp, agent4_gap

# Pesos do Agent-Readiness Score (ARS)
PESOS = {
    "performance": 0.40,
    "schema":      0.40,
    "conteudo":    0.20,
}

CLASSIFICACOES = [
    (81, 100, "otimizado",  "🏆 Agent-ready — Pacman come o ghost"),
    (61, 80,  "legivel",    "✅ Legível — agente consegue parsear e recomendar"),
    (31, 60,  "em_risco",   "⚠️ Em risco — dados incompletos"),
    (0,  30,  "fantasma",   "👻 Fantasma — invisível para agentes"),
]


def classificar_ars(score: int) -> dict:
    for min_s, max_s, slug, descricao in CLASSIFICACOES:
        if min_s <= score <= max_s:
            return {"slug": slug, "descricao": descricao}
    return {"slug": "fantasma", "descricao": "👻 Fantasma"}


def calcular_ars(p_crux: int, p_schema: int, p_nlp: int) -> int:
    """Calcula o Agent-Readiness Score com os pesos definidos."""
    score = (
        p_crux   * PESOS["performance"] +
        p_schema * PESOS["schema"] +
        p_nlp    * PESOS["conteudo"]
    )
    return round(score)


def analisar(url: str, query: str = None) -> dict:
    """
    Função principal do orquestrador.
    Roda Agentes em paralelo, depois Agente 2.5, depois Agente 4.
    """
    print(f"\n🔍 Analisando: {url[:60]}...")

    # ── Agentes em paralelo ──────────────────────────
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        future_crux      = executor.submit(agent1_crux.run, url)
        future_pagespeed = executor.submit(agent1_pagespeed.run, url)
        future_schema    = executor.submit(agent2_schema.run, url)
        future_nlp       = executor.submit(agent3_nlp.run, url)

        resultado_crux      = future_crux.result()
        resultado_pagespeed = future_pagespeed.result()
        resultado_schema    = future_schema.result()
        resultado_nlp       = future_nlp.result()

    print(f"  ✓ CrUX Score:        {resultado_crux['score']}/100")
    print(f"  ✓ PageSpeed Score:   {resultado_pagespeed['score']}/100")
    print(f"  ✓ Schema Score:      {resultado_schema['score']}/100")
    print(f"  ✓ NLP Score:         {resultado_nlp['score']}/100")

    # ── Agente 2.5 — Schema Quality ───────────────────────────
    print("  ✓ Analisando qualidade do Schema...")
    resultado_schema_quality = agent2_5_schema_quality.run(resultado_schema)
    
    print(f"    └─ Structure: {resultado_schema_quality.get('structure_score', 0)}/100")
    print(f"    └─ Quality:   {resultado_schema_quality.get('quality_score', 0)}/100")

    # ── Agente 4 — Gap Analysis ───────────────────────────────
    print("  ✓ Rodando Gap Analysis...")
    resultado_gap = agent4_gap.run(url, resultado_schema, resultado_nlp, query)

    # ── Calcula ARS (usa quality_score do Schema) ─────────────
    # IMPORTANTE: Agora usamos o quality_score ao invés do structure_score
    schema_score_para_ars = resultado_schema_quality.get('quality_score', resultado_schema['score'])
    
    ars = calcular_ars(
        resultado_crux["score"],
        schema_score_para_ars,  # ← Mudou aqui!
        resultado_nlp["score"]
    )
    classificacao = classificar_ars(ars)

    print(f"\n  🎯 Agent-Readiness Score: {ars}/100 — {classificacao['slug'].upper()}")

    return {
        "url": url,
        "ars": ars,
        "classificacao": classificacao,
        "agentes": {
            "crux":           resultado_crux,
            "pagespeed":      resultado_pagespeed,
            "schema":         resultado_schema,
            "schema_quality": resultado_schema_quality,  # ← NOVO
            "conteudo":       resultado_nlp,
            "gap_analysis":   resultado_gap,
        },
        "recomendacoes": resultado_gap.get("recomendacoes", []),
        "pesos_utilizados": PESOS,
        "nota": "Pesos são hipótese v0.1 — serão validados pela pesquisa ICMC/USP. Schema agora usa quality_score (não só structure)."
    }


# ─────────────────────────────────────────
# EXECUÇÃO DIRETA (teste manual)
# ─────────────────────────────────────────

if __name__ == "__main__":
    import sys
    import json

    url = sys.argv[1] if len(sys.argv) > 1 else \
        "https://www.natura.com.br/p/serum-intensivo-multiclareador-chronos-derma-30-ml/NATBRA-169222"

    resultado = analisar(url)

    print("\n" + "="*60)
    print("RESULTADO COMPLETO")
    print("="*60)
    print(json.dumps(resultado, indent=2, ensure_ascii=False, default=str))
