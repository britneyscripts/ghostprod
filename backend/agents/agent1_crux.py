"""
ghostprod — agents/agent1_crux.py
─────────────────────────────────────────────────────────
Agente 1: Performance Score via CrUX API.
Retorna score 0-100 baseado nos Core Web Vitals reais.
"""

from crux_pipeline import analisar_url


def run(url: str) -> dict:
    """
    Executa o Agente 1.
    Retorna performance_score e métricas detalhadas.
    """
    resultado = analisar_url(url)

    if resultado["status"] == "sem_dados":
        return {
            "agente": "agent1_crux",
            "score": 0,
            "status": "sem_dados",
            "motivo": "URL sem dados suficientes na CrUX API (baixo tráfego)",
            "metricas": {}
        }

    return {
        "agente": "agent1_crux",
        "score": resultado["performance_score"],
        "status": "ok",
        "lcp_p75":  resultado["lcp_p75"],
        "inp_p75":  resultado["inp_p75"],
        "cls_p75":  resultado["cls_p75"],
        "ttfb_p75": resultado["ttfb_p75"],
        "metricas": resultado["metricas"]
    }
