"""
ghostprod — agents/agent3_nlp.py
─────────────────────────────────────────────────────────
Agente 3: NLP Score — densidade de atributos técnicos.
Mede se a descrição tem dados verificáveis (atributos
factuais) ou é só marketing gloss.

Diferença central:
  Marketing gloss:  "Produto de alta qualidade para pele radiante"
  Atributo factual: "Niacinamida 10%, volume 30ml, FPS 50"
"""

import re
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup


# Padrões de atributos técnicos verificáveis
# Baseado em análise de PDPs de beleza brasileiras
PADROES_ATRIBUTOS = [
    # Concentrações e ingredientes ativos
    r"\b\d+[\.,]?\d*\s*%",               # "10%", "5,5%"
    r"\b\d+\s*mg\b",                     # "50mg"
    r"\b\d+\s*ml\b",                     # "30ml", "100 ml"
    r"\b\d+\s*g\b",                      # "50g"
    r"\b\d+\s*ui\b",                     # "1000 UI" (vitaminas)
    # Ingredientes INCI / técnicos
    r"\bniacinamida\b",
    r"\bácido\s+\w+",                    # "ácido hialurônico", "ácido glicólico"
    r"\bretinol\b",
    r"\bvitamina\s+[a-z]\b",
    r"\bcolágeno\b",
    r"\bpeptídeo",
    r"\bcerâmida",
    r"\bspf\s*\d+",                      # "SPF 50"
    r"\bfps\s*\d+",                      # "FPS 50" (BR)
    r"\bpa\+{1,4}",                      # "PA+++"
    r"\bpH\s*[\d,\.]+",                  # "pH 5,5"
    # Tipos de pele
    r"pele\s+(oleosa|seca|mista|sensível|normal)",
    r"tipo\s+de\s+pele",
    # Certificações
    r"\beverificado\s+dermatologicamente\b",
    r"\btestado\s+dermatologicamente\b",
    r"\bhipoalergênico\b",
    r"\bcruelty.free\b",
    r"\bvegano\b",
    # Dados numéricos de resultado
    r"\b\d+\s*x\s+mais",                 # "3x mais hidratante"
    r"\b\d+\s*horas\s+de",              # "24 horas de hidratação"
    r"\b\d+\s*dias",                     # "em 7 dias"
    r"reduz\s+\d+",                      # "reduz 84%"
]

# Palavras de marketing gloss (sem valor informacional para agentes)
MARKETING_GLOSS = [
    "incrível", "maravilhoso", "fantástico", "perfeito",
    "revolucionário", "inovador", "exclusivo", "único",
    "premium", "luxo", "sofisticado", "poderoso",
    "transformador", "milagroso", "mágico",
    "alta qualidade", "melhor do mercado",
]


def extrair_texto_pdp(url: str) -> str:
    """Extrai o texto da PDP após renderização JavaScript."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(5000)
            html = page.content()
        finally:
            browser.close()

    soup = BeautifulSoup(html, "html.parser")

    # Remove scripts, estilos e navegação
    for tag in soup(["script", "style", "nav", "header", "footer"]):
        tag.decompose()

    return soup.get_text(separator=" ", strip=True)


def calcular_nlp_score(texto: str) -> dict:
    """
    Calcula o NLP score baseado na densidade de atributos técnicos.
    """
    texto_lower = texto.lower()
    palavras = texto_lower.split()
    total_palavras = len(palavras) if palavras else 1

    # Conta atributos técnicos encontrados
    atributos_encontrados = []
    for padrao in PADROES_ATRIBUTOS:
        matches = re.findall(padrao, texto_lower, re.IGNORECASE)
        if matches:
            atributos_encontrados.extend(matches)

    # Conta marketing gloss
    gloss_encontrado = []
    for termo in MARKETING_GLOSS:
        if termo in texto_lower:
            gloss_encontrado.append(termo)

    # Densidade de atributos (atributos por 100 palavras)
    densidade = (len(atributos_encontrados) / total_palavras) * 100

    # Score baseado na densidade e penalidade por gloss
    # Densidade ideal: 3+ atributos por 100 palavras = score 100
    score_base = min(100, round(densidade * 33))

    # Penalidade por excesso de marketing gloss
    penalidade = min(20, len(gloss_encontrado) * 3)
    score_final = max(0, score_base - penalidade)

    return {
        "score": score_final,
        "atributos_encontrados": list(set(atributos_encontrados))[:20],
        "total_atributos": len(atributos_encontrados),
        "marketing_gloss": gloss_encontrado,
        "densidade_atributos": round(densidade, 2),
        "total_palavras": total_palavras,
    }


def run(url: str) -> dict:
    """
    Executa o Agente 3.
    Retorna nlp_score e análise de conteúdo.
    """
    texto = extrair_texto_pdp(url)
    resultado = calcular_nlp_score(texto)

    return {
        "agente": "agent3_nlp",
        "score": resultado["score"],
        "atributos_encontrados": resultado["atributos_encontrados"],
        "total_atributos": resultado["total_atributos"],
        "marketing_gloss": resultado["marketing_gloss"],
        "densidade_atributos": resultado["densidade_atributos"],
        "diagnostico": (
            "rico em atributos técnicos" if resultado["score"] >= 60
            else "marketing gloss dominante" if resultado["score"] < 30
            else "atributos técnicos presentes mas insuficientes"
        )
    }
