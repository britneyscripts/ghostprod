"""
ghostprod — agents/agent2_schema.py
─────────────────────────────────────────────────────────
Agente 2: Schema.org Score via Playwright.
Renderiza a PDP com browser real (resolve CSR/VTEX IO)
e avalia completude do JSON-LD de Product.
"""

import json
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

# Campos obrigatórios do Schema de Produto
# Baseado nas diretrizes do Google para Rich Results
CAMPOS_OBRIGATORIOS = [
    "name",
    "description",
    "image",
    "sku",
    "offers",
]

# Campos recomendados para agent-readiness
# Quanto mais campos, mais o agente consegue responder queries complexas
CAMPOS_RECOMENDADOS = [
    "brand",
    "aggregateRating",
    "review",
    "gtin8",        # código de barras — identificação universal
    "gtin13",
    "mpn",
    "color",
    "material",
    "audience",
    "category",
    "subjectOf",    # FAQPage aninhada (ex: Jumbo) — gold standard
]


def extrair_schema_produto(url: str, timeout_ms: int = 15000) -> dict:
    """
    Abre a PDP com Playwright, espera JS renderizar,
    extrai e avalia o Schema.org de Product.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            page.goto(url, wait_until="domcontentloaded", timeout=30000)

            # Tenta esperar o Schema aparecer (mais inteligente que timeout fixo)
            try:
                page.wait_for_selector(
                    'script[type="application/ld+json"]',
                    timeout=timeout_ms
                )
            except Exception:
                # Se não aparecer, aguarda tempo fixo
                page.wait_for_timeout(8000)

            html = page.content()

        finally:
            browser.close()

    # Parseia o HTML renderizado
    soup = BeautifulSoup(html, "html.parser")
    scripts = soup.find_all("script", type="application/ld+json")

    todos_schemas = []
    for s in scripts:
        try:
            dados = json.loads(s.string)
            # Lida com @graph (estrutura aninhada)
            if isinstance(dados, dict) and "@graph" in dados:
                todos_schemas.extend(dados["@graph"])
            else:
                todos_schemas.append(dados)
        except Exception:
            continue

    # Encontra o schema de Product
    schema_produto = None
    for d in todos_schemas:
        tipo = d.get("@type", "")
        if tipo == "Product" or (isinstance(tipo, list) and "Product" in tipo):
            schema_produto = d
            break

    return schema_produto, todos_schemas


def avaliar_completude(schema: dict) -> dict:
    """
    Avalia completude do Schema de Produto.
    Retorna score 0-100 e lista de campos presentes/ausentes.
    """
    if not schema:
        return {
            "score": 0,
            "campos_presentes": [],
            "campos_ausentes": CAMPOS_OBRIGATORIOS + CAMPOS_RECOMENDADOS,
            "obrigatorios_ok": 0,
            "recomendados_ok": 0,
        }

    presentes = []
    ausentes = []

    todos_campos = CAMPOS_OBRIGATORIOS + CAMPOS_RECOMENDADOS
    for campo in todos_campos:
        if schema.get(campo):
            presentes.append(campo)
        else:
            ausentes.append(campo)

    obrigatorios_ok = sum(1 for c in CAMPOS_OBRIGATORIOS if c in presentes)
    recomendados_ok = sum(1 for c in CAMPOS_RECOMENDADOS if c in presentes)

    # Score: obrigatórios valem 70%, recomendados valem 30%
    score_obrigatorios = (obrigatorios_ok / len(CAMPOS_OBRIGATORIOS)) * 70
    score_recomendados = (recomendados_ok / len(CAMPOS_RECOMENDADOS)) * 30
    score_total = round(score_obrigatorios + score_recomendados)

    return {
        "score": score_total,
        "campos_presentes": presentes,
        "campos_ausentes": ausentes,
        "obrigatorios_ok": obrigatorios_ok,
        "obrigatorios_total": len(CAMPOS_OBRIGATORIOS),
        "recomendados_ok": recomendados_ok,
        "recomendados_total": len(CAMPOS_RECOMENDADOS),
    }


def run(url: str) -> dict:
    """
    Executa o Agente 2.
    Retorna schema_score e avaliação de completude.
    """
    schema_produto, todos_schemas = extrair_schema_produto(url)
    avaliacao = avaliar_completude(schema_produto)

    return {
        "agente": "agent2_schema",
        "score": avaliacao["score"],
        "tem_schema_produto": schema_produto is not None,
        "total_schemas": len(todos_schemas),
        "completude": avaliacao,
        "schema_raw": schema_produto,
    }
