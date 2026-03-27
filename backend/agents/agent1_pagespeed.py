"""
ghostprod — agents/agent1_pagespeed.py
─────────────────────────────────────────────────────────
Agente 1 (v2): Performance Score via PageSpeed Insights API.

Diferença em relação ao CrUX:
  PageSpeed (este arquivo) → dado sintético (lab)
    → funciona para QUALQUER URL
    → Lighthouse score + LCP, CLS, TBT, FCP, SI
    → roda agora, resultado imediato
    → base do score de performance em tempo real

  CrUX (crux_pipeline.py) → dado de campo (real)
    → só URLs com tráfego mínimo de usuários Chrome
    → percentil p75 de usuários reais
    → coletado diariamente e salvo com timestamp
    → base do gráfico histórico (como DebugBear)

Para a v0.1: usamos PageSpeed para o score em tempo real.
O histórico CrUX cresce com o tempo — começa hoje.

Uso:
    python agent1_pagespeed.py https://natura.com.br/...
"""

import os
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

PSI_API_KEY = os.getenv("PSI_API_KEY")
PSI_ENDPOINT = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"

# Thresholds Core Web Vitals — Google 2024
# https://web.dev/articles/defining-core-web-vitals-thresholds
THRESHOLDS = {
    "lcp":  {"bom": 2500,  "ruim": 4000},   # ms — Largest Contentful Paint
    "cls":  {"bom": 0.1,   "ruim": 0.25},   # score — Cumulative Layout Shift
    "tbt":  {"bom": 200,   "ruim": 600},    # ms — Total Blocking Time (proxy INP)
    "fcp":  {"bom": 1800,  "ruim": 3000},   # ms — First Contentful Paint
    "si":   {"bom": 3400,  "ruim": 5800},   # ms — Speed Index
}


def classificar(nome, valor):
    """Classifica métrica como bom / precisa_melhorar / ruim."""
    if nome not in THRESHOLDS or valor is None:
        return "sem_dados"
    t = THRESHOLDS[nome]
    if valor <= t["bom"]:
        return "bom"
    elif valor <= t["ruim"]:
        return "precisa_melhorar"
    return "ruim"


def get_pagespeed(url, strategy="MOBILE"):
    """
    Chama a PageSpeed Insights API v5.
    strategy: MOBILE ou DESKTOP
    Timeout de 60s — PSI pode demorar para sites lentos.
    """
    params = {
        "url": url,
        "strategy": strategy,
        "category": "performance",
        "locale": "pt-BR",
    }
    if PSI_API_KEY:
        params["key"] = PSI_API_KEY

    try:
        response = requests.get(PSI_ENDPOINT, params=params, timeout=60)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        return {"erro": "timeout", "url": url}
    except requests.exceptions.RequestException as e:
        return {"erro": str(e), "url": url}


def processar_psi(dados, url, strategy):
    """
    Extrai métricas relevantes da resposta PSI.
    Retorna score 0-100 e breakdown por métrica.
    """
    if "erro" in dados:
        return {
            "url": url,
            "status": "erro",
            "erro": dados["erro"],
            "performance_score": 0,
            "metricas": {}
        }

    lighthouse = dados.get("lighthouseResult", {})

    # Score geral de performance (0-1 → 0-100)
    categories = lighthouse.get("categories", {})
    perf_score = categories.get("performance", {}).get("score")
    performance_score = round(perf_score * 100) if perf_score is not None else 0

    # Métricas individuais
    audits = lighthouse.get("audits", {})

    def extrair_metrica(key):
        audit = audits.get(key, {})
        return {
            "valor": audit.get("numericValue"),
            "display": audit.get("displayValue", "—"),
            "score": audit.get("score"),
        }

    lcp_raw = extrair_metrica("largest-contentful-paint")
    cls_raw = extrair_metrica("cumulative-layout-shift")
    tbt_raw = extrair_metrica("total-blocking-time")
    fcp_raw = extrair_metrica("first-contentful-paint")
    si_raw  = extrair_metrica("speed-index")

    metricas = {
        "lcp": {
            **lcp_raw,
            "classificacao": classificar("lcp", lcp_raw["valor"]),
            "nome": "Largest Contentful Paint",
        },
        "cls": {
            **cls_raw,
            "classificacao": classificar("cls", cls_raw["valor"]),
            "nome": "Cumulative Layout Shift",
        },
        "tbt": {
            **tbt_raw,
            "classificacao": classificar("tbt", tbt_raw["valor"]),
            "nome": "Total Blocking Time",
        },
        "fcp": {
            **fcp_raw,
            "classificacao": classificar("fcp", fcp_raw["valor"]),
            "nome": "First Contentful Paint",
        },
        "si": {
            **si_raw,
            "classificacao": classificar("si", si_raw["valor"]),
            "nome": "Speed Index",
        },
    }

    return {
        "url": url,
        "status": "ok",
        "strategy": strategy,
        "data_coleta": datetime.utcnow().isoformat(),
        "performance_score": performance_score,
        "metricas": metricas,
        # Atalhos para os campos mais usados
        "lcp_ms":     lcp_raw["valor"],
        "cls_score":  cls_raw["valor"],
        "tbt_ms":     tbt_raw["valor"],
        "fcp_ms":     fcp_raw["valor"],
        "lcp_display": lcp_raw["display"],
        "cls_display": cls_raw["display"],
        "tbt_display": tbt_raw["display"],
    }


def analisar_url(url, strategy="MOBILE"):
    """Função principal — chama PSI e retorna resultado processado."""
    dados = get_pagespeed(url, strategy)
    return processar_psi(dados, url, strategy)


def run(url: str) -> dict:
    """
    Interface padrão do orquestrador.
    Retorna performance_score e métricas detalhadas.
    """
    resultado = analisar_url(url, strategy="MOBILE")

    if resultado["status"] == "erro":
        return {
            "agente": "agent1_pagespeed",
            "score": 0,
            "status": "erro",
            "erro": resultado.get("erro", "erro desconhecido"),
            "metricas": {}
        }

    return {
        "agente": "agent1_pagespeed",
        "score": resultado["performance_score"],
        "status": "ok",
        "strategy": resultado["strategy"],
        "lcp_ms":    resultado["lcp_ms"],
        "cls_score": resultado["cls_score"],
        "tbt_ms":    resultado["tbt_ms"],
        "fcp_ms":    resultado["fcp_ms"],
        "lcp_display": resultado["lcp_display"],
        "cls_display": resultado["cls_display"],
        "tbt_display": resultado["tbt_display"],
        "metricas": resultado["metricas"],
        "nota": "dado sintético (lab) — Lighthouse via PSI API"
    }


# ─────────────────────────────────────────
# EXECUÇÃO DIRETA (teste manual)
# ─────────────────────────────────────────

if __name__ == "__main__":
    import sys
    import json

    url = sys.argv[1] if len(sys.argv) > 1 else \
        "https://www.natura.com.br/p/serum-intensivo-multiclareador-chronos-derma-30-ml/NATBRA-169222"

    print(f"\n🔍 PageSpeed Insights API")
    print(f"   URL: {url[:70]}...")
    print(f"   Aguarde — pode demorar até 60s...\n")

    resultado = run(url)

    print(f"✅ Performance Score: {resultado['score']}/100")
    print(f"   ({resultado.get('nota', '')})")
    print()

    metricas = resultado.get("metricas", {})
    for key, dados in metricas.items():
        emoji = {"bom": "✅", "precisa_melhorar": "⚠️", "ruim": "❌"}.get(
            dados.get("classificacao", ""), "—"
        )
        print(f"   {emoji} {dados['nome']}: {dados['display']} ({dados['classificacao']})")

    print()
    print(json.dumps(resultado, indent=2, ensure_ascii=False, default=str))
