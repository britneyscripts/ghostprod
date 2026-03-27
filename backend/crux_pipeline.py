"""
ghostprod — crux_pipeline.py
─────────────────────────────────────────────────────────
Batch diário: puxa dados da CrUX API e salva no BigQuery.
Rodar uma vez por dia via Cloud Scheduler.

A CrUX API agrega dados reais dos últimos 28 dias de
usuários Chrome. Os dados só mudam uma vez por dia —
por isso não faz sentido chamar em tempo real.

Uso:
    python crux_pipeline.py --url https://natura.com.br/...
    python crux_pipeline.py --file urls.txt
"""

import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

CRUX_API_KEY = os.getenv("CRUX_API_KEY")
CRUX_ENDPOINT = "https://chromeuxreport.googleapis.com/v1/records:queryRecord"

# Métricas que queremos (percentil 75 — padrão Google/DebugBear)
METRICAS = [
    "largest_contentful_paint",       # LCP
    "first_input_delay",              # FID (legado)
    "cumulative_layout_shift",        # CLS
    "interaction_to_next_paint",      # INP (novo padrão desde mar/2024)
    "experimental_time_to_first_byte" # TTFB
]

# Thresholds Core Web Vitals (Google)
THRESHOLDS = {
    "largest_contentful_paint":       {"bom": 2500,  "ruim": 4000},  # ms
    "interaction_to_next_paint":      {"bom": 200,   "ruim": 500},   # ms
    "cumulative_layout_shift":        {"bom": 0.1,   "ruim": 0.25},  # score
    "experimental_time_to_first_byte":{"bom": 800,   "ruim": 1800},  # ms
}


def classificar_metrica(nome, valor_p75):
    """Classifica uma métrica como 'bom', 'precisa melhorar' ou 'ruim'."""
    if nome not in THRESHOLDS:
        return "sem_threshold"
    t = THRESHOLDS[nome]
    if valor_p75 <= t["bom"]:
        return "bom"
    elif valor_p75 <= t["ruim"]:
        return "precisa_melhorar"
    else:
        return "ruim"


def calcular_performance_score(metricas_classificadas):
    """
    Calcula score de performance 0-100 baseado nas classificações.
    Peso: INP 30% | LCP 30% | TTFB 25% | CLS 15%
    Segue a lógica do DebugBear / Google PageSpeed.
    """
    pesos = {
        "interaction_to_next_paint":       0.30,
        "largest_contentful_paint":        0.30,
        "experimental_time_to_first_byte": 0.25,
        "cumulative_layout_shift":         0.15,
    }
    pontos = {"bom": 100, "precisa_melhorar": 50, "ruim": 0, "sem_threshold": 50}

    score = 0
    peso_total = 0
    for metrica, peso in pesos.items():
        if metrica in metricas_classificadas:
            classificacao = metricas_classificadas[metrica]["classificacao"]
            score += pontos[classificacao] * peso
            peso_total += peso

    if peso_total == 0:
        return 0
    return round(score / peso_total) if peso_total < 1 else round(score)


def get_crux_data(url, form_factor="PHONE"):
    """
    Chama a CrUX API para uma URL e retorna os dados de campo.
    form_factor: PHONE | DESKTOP | ALL_FORM_FACTORS
    """
    payload = {
        "url": url,
        "formFactor": form_factor,
        "metrics": METRICAS
    }

    params = {}
    if CRUX_API_KEY:
        params["key"] = CRUX_API_KEY

    try:
        response = requests.post(
            CRUX_ENDPOINT,
            json=payload,
            params=params,
            timeout=15
        )

        if response.status_code == 404:
            # URL não tem dados suficientes na CrUX
            return {"erro": "sem_dados_crux", "url": url}

        response.raise_for_status()
        return response.json()

    except requests.exceptions.Timeout:
        return {"erro": "timeout", "url": url}
    except requests.exceptions.RequestException as e:
        return {"erro": str(e), "url": url}


def processar_resposta_crux(dados_crux, url):
    """
    Processa a resposta bruta da CrUX API e extrai:
    - valor p75 de cada métrica
    - classificação (bom/precisa_melhorar/ruim)
    - score de performance 0-100
    """
    if "erro" in dados_crux:
        return {
            "url": url,
            "status": "sem_dados",
            "erro": dados_crux["erro"],
            "performance_score": None,
            "metricas": {}
        }

    record = dados_crux.get("record", {})
    metrics_raw = record.get("metrics", {})

    metricas_processadas = {}
    for nome_metrica, dados in metrics_raw.items():
        # p75 é o percentil 75 — padrão Core Web Vitals
        percentis = dados.get("percentiles", {})
        p75 = percentis.get("p75")

        if p75 is not None:
            classificacao = classificar_metrica(nome_metrica, p75)
            metricas_processadas[nome_metrica] = {
                "p75": p75,
                "classificacao": classificacao,
                "histograma": dados.get("histogram", [])
            }

    performance_score = calcular_performance_score(metricas_processadas)

    return {
        "url": url,
        "status": "ok",
        "data_coleta": datetime.utcnow().isoformat(),
        "form_factor": record.get("key", {}).get("formFactor", "PHONE"),
        "performance_score": performance_score,
        "metricas": metricas_processadas,
        # Atalhos para os campos mais usados
        "lcp_p75":  metricas_processadas.get("largest_contentful_paint", {}).get("p75"),
        "inp_p75":  metricas_processadas.get("interaction_to_next_paint", {}).get("p75"),
        "cls_p75":  metricas_processadas.get("cumulative_layout_shift", {}).get("p75"),
        "ttfb_p75": metricas_processadas.get("experimental_time_to_first_byte", {}).get("p75"),
    }


def analisar_url(url):
    """
    Função principal — chama CrUX e retorna resultado processado.
    Usada pelo orchestrator em tempo real (lê do cache se disponível).
    """
    dados_brutos = get_crux_data(url)
    return processar_resposta_crux(dados_brutos, url)


# ─────────────────────────────────────────
# EXECUÇÃO DIRETA (batch ou teste manual)
# ─────────────────────────────────────────

if __name__ == "__main__":
    import sys

    urls_teste = [
        "https://www.natura.com.br/p/serum-intensivo-multiclareador-chronos-derma-30-ml/NATBRA-169222",
        "https://www.boticario.com.br/serum-de-alta-potencia-vitamina-c-10-botik-30ml-v2/",
    ]

    # Se passou URL como argumento, usa ela
    if len(sys.argv) > 1:
        urls_teste = [sys.argv[1]]

    for url in urls_teste:
        print(f"\n{'='*60}")
        print(f"URL: {url[:60]}...")
        print(f"{'='*60}")

        resultado = analisar_url(url)

        if resultado["status"] == "sem_dados":
            print(f"⚠️  Sem dados CrUX para esta URL: {resultado['erro']}")
            print("   (URL pode ter pouco tráfego ou não estar indexada)")
        else:
            print(f"\n✅ Performance Score: {resultado['performance_score']}/100")
            print(f"\n   LCP  (p75): {resultado['lcp_p75']} ms")
            print(f"   INP  (p75): {resultado['inp_p75']} ms")
            print(f"   CLS  (p75): {resultado['cls_p75']}")
            print(f"   TTFB (p75): {resultado['ttfb_p75']} ms")
            print()
            for nome, dados in resultado["metricas"].items():
                emoji = {"bom": "✅", "precisa_melhorar": "⚠️", "ruim": "❌"}.get(
                    dados["classificacao"], "—"
                )
                print(f"   {emoji} {nome}: {dados['p75']} ({dados['classificacao']})")
