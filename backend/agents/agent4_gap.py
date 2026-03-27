"""
ghostprod — agents/agent4_gap.py
─────────────────────────────────────────────────────────
Agente 4: Gap Analysis via Claude API.
Simula o raciocínio de um agente de IA ao tentar
responder uma query de produto com os dados disponíveis.

Responde: "Dado este conteúdo, o produto seria
incluído em uma recomendação para X?"
Se não — identifica exatamente qual campo está faltando.
"""

import os
import anthropic
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Queries típicas de consumidor BR no setor de beleza
QUERIES_PADRAO = [
    "sérum para pele oleosa com niacinamida",
    "hidratante facial com ácido hialurônico para pele seca",
    "protetor solar FPS 50 para uso diário",
    "creme anti-idade com retinol",
    "vitamina C para manchas",
]


def montar_contexto(schema_resultado: dict, nlp_resultado: dict) -> str:
    """Monta o contexto do produto a partir dos resultados dos Agentes 2 e 3."""
    schema = schema_resultado.get("schema_raw") or {}
    atributos = nlp_resultado.get("atributos_encontrados", [])

    contexto = f"""
DADOS ESTRUTURADOS (Schema.org):
- Nome: {schema.get('name', 'ausente')}
- Descrição: {str(schema.get('description', 'ausente'))[:300]}
- Marca: {schema.get('brand', {}).get('name', 'ausente') if isinstance(schema.get('brand'), dict) else schema.get('brand', 'ausente')}
- Categoria: {schema.get('category', 'ausente')}
- Preço: {schema.get('offers', {}).get('price', 'ausente') if isinstance(schema.get('offers'), dict) else 'ausente'}
- Disponibilidade: {schema.get('offers', {}).get('availability', 'ausente') if isinstance(schema.get('offers'), dict) else 'ausente'}
- Rating: {schema.get('aggregateRating', {}).get('ratingValue', 'ausente') if isinstance(schema.get('aggregateRating'), dict) else 'ausente'}
- Campos presentes: {', '.join(schema_resultado.get('completude', {}).get('campos_presentes', []))}
- Campos ausentes: {', '.join(schema_resultado.get('completude', {}).get('campos_ausentes', []))}

ATRIBUTOS TÉCNICOS ENCONTRADOS NO CONTEÚDO:
{', '.join(atributos) if atributos else 'Nenhum atributo técnico verificável encontrado'}
""".strip()

    return contexto


def run(url: str, schema_resultado: dict, nlp_resultado: dict,
        query: str = None) -> dict:
    """
    Executa o Agente 4.
    Simula um agente de IA tentando responder a query com os dados disponíveis.
    """
    if not ANTHROPIC_API_KEY:
        return {
            "agente": "agent4_gap",
            "score": 0,
            "status": "sem_chave_api",
            "gap_analysis": "ANTHROPIC_API_KEY não configurada",
            "recomendacoes": []
        }

    if not query:
        query = QUERIES_PADRAO[0]

    contexto = montar_contexto(schema_resultado, nlp_resultado)

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    prompt = f"""Você é um agente de IA de compras que precisa recomendar produtos para consumidores.

Um consumidor pediu: "{query}"

Você chegou nesta página de produto e encontrou os seguintes dados:

{contexto}

Analise se você consegue recomendar este produto para a query acima.

Responda em JSON com exatamente esta estrutura:
{{
  "pode_recomendar": true/false,
  "confianca": 0-100,
  "motivo": "explicação em 1-2 frases",
  "campos_faltando": ["lista", "de", "campos", "ausentes", "que", "impediriam", "recomendacao"],
  "recomendacoes": [
    "Ação específica 1 para melhorar a legibilidade",
    "Ação específica 2",
    "Ação específica 3"
  ]
}}

Seja direto e técnico. Foque em dados verificáveis, não em marketing."""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )

        resposta_texto = message.content[0].text

        # Extrai o JSON da resposta
        import json
        import re
        json_match = re.search(r'\{.*\}', resposta_texto, re.DOTALL)
        if json_match:
            analise = json.loads(json_match.group())
        else:
            analise = {
                "pode_recomendar": False,
                "confianca": 0,
                "motivo": resposta_texto,
                "campos_faltando": [],
                "recomendacoes": []
            }

        # Score do agente 4: baseado na confiança de recomendação
        score = analise.get("confianca", 0)

        return {
            "agente": "agent4_gap",
            "score": score,
            "status": "ok",
            "query_testada": query,
            "pode_recomendar": analise.get("pode_recomendar", False),
            "confianca": analise.get("confianca", 0),
            "motivo": analise.get("motivo", ""),
            "campos_faltando": analise.get("campos_faltando", []),
            "recomendacoes": analise.get("recomendacoes", []),
        }

    except Exception as e:
        return {
            "agente": "agent4_gap",
            "score": 0,
            "status": "erro",
            "erro": str(e),
            "recomendacoes": []
        }
