"""
ghostprod — agents/agent2_5_schema_quality.py
─────────────────────────────────────────────────────────
Agente 2.5: Schema Quality Scorer

PROBLEMA QUE RESOLVE:
  Agente 2 diz: "Schema existe e é válido" → 84% ✅
  MAS o conteúdo pode ser marketing gloss inútil para agentes!
  
EXEMPLO:
  {
    "@type": "Product",
    "description": "• menos 84% de manchas* em duas semanas¹..."
  }
  
  ✅ Estrutura válida (JSON correto, campos certos)
  ❌ Conteúdo inútil (marketing gloss, sem dados técnicos)

ESTE AGENTE:
  - Pega o Schema do Agente 2
  - Analisa QUALIDADE do conteúdo (não só estrutura)
  - Penaliza marketing gloss, campos vazios, falta de dados técnicos
  - Retorna 2 scores separados:
    * structure_score: Schema existe e é válido?
    * quality_score: Conteúdo é útil para agentes?

Uso:
    python agent2_5_schema_quality.py
"""

import re
import spacy

# Carrega modelo spaCy PT (assumindo que já foi instalado)
try:
    nlp = spacy.load("pt_core_news_sm")
except OSError:
    print("⚠️ Modelo spaCy não encontrado. Rode: python -m spacy download pt_core_news_sm")
    nlp = None

# ════════════════════════════════════════════════════════
# CAMPOS ESPERADOS NO SCHEMA.ORG PRODUCT
# ════════════════════════════════════════════════════════
# https://schema.org/Product

CAMPOS_ESSENCIAIS = {
    "name": 10,               # Nome do produto
    "description": 15,        # Descrição
    "brand": 10,              # Marca
    "offers": 10,             # Preço/disponibilidade
}

CAMPOS_DESEJÁVEIS = {
    "image": 5,               # Imagem
    "sku": 5,                 # SKU
    "gtin13": 5,              # Código de barras (EAN)
    "category": 5,            # Categoria
    "additionalProperty": 20, # ← CRÍTICO para dados técnicos
    "material": 10,           # Materiais/ingredientes
    "review": 5,              # Avaliações
    "aggregateRating": 5,     # Rating agregado
}

# ════════════════════════════════════════════════════════
# PADRÕES DE MARKETING GLOSS
# ════════════════════════════════════════════════════════

MARKETING_PATTERNS = [
    r"\d+%",                  # Porcentagens (ex: "84% de redução")
    r"\*+",                   # Asteriscos (ex: "menos manchas*")
    r"¹²³⁴⁵⁶⁷⁸⁹",              # Superscripts (notas de rodapé)
    r"testado e aprovado",
    r"dermatologicamente testado",
    r"clinicamente comprovado",
    r"resultado em \d+ (dias|semanas|meses)",
    r"imediatamente",
    r"instantâneo",
]


def calcular_marketing_gloss_ratio(texto: str) -> float:
    """
    Calcula % do texto que é marketing gloss.
    
    Returns:
        float entre 0.0 (sem gloss) e 1.0 (100% gloss)
    """
    if not texto:
        return 0.0
    
    gloss_chars = 0
    for pattern in MARKETING_PATTERNS:
        matches = re.findall(pattern, texto, re.IGNORECASE)
        for match in matches:
            gloss_chars += len(match)
    
    return min(1.0, gloss_chars / len(texto))


def analisar_description(description: str) -> dict:
    """
    Analisa qualidade do campo 'description' do Schema.
    
    Penalidades:
      - Marketing gloss alto (>30%)
      - Texto curto demais (<50 chars)
      - Falta de substantivos técnicos
    """
    if not description:
        return {
            "score": 0,
            "problema": "description vazio",
            "penalidade": -15
        }
    
    # Detecta marketing gloss
    gloss_ratio = calcular_marketing_gloss_ratio(description)
    
    if gloss_ratio > 0.3:
        return {
            "score": 40,
            "problema": "description com marketing gloss (símbolos, %, notas de rodapé)",
            "penalidade": -10,
            "gloss_ratio": round(gloss_ratio * 100)
        }
    
    # Texto muito curto
    if len(description) < 50:
        return {
            "score": 50,
            "problema": "description muito curta (<50 chars)",
            "penalidade": -5
        }
    
    # Analisa densidade de substantivos (proxy de informação técnica)
    if nlp:
        doc = nlp(description[:500])  # Limita pra não explodir memória
        substantivos = [token for token in doc if token.pos_ == "NOUN"]
        densidade_substantivos = len(substantivos) / len(doc) if len(doc) > 0 else 0
        
        if densidade_substantivos < 0.15:
            return {
                "score": 60,
                "problema": "description com poucos substantivos (baixa densidade técnica)",
                "penalidade": -5,
                "densidade_substantivos": round(densidade_substantivos * 100)
            }
    
    # Description OK
    return {
        "score": 100,
        "problema": None,
        "penalidade": 0
    }


def analisar_additional_property(additional_property: list) -> dict:
    """
    Analisa qualidade do campo 'additionalProperty'.
    
    Este é o campo MAIS IMPORTANTE para agentes — é onde ficam
    atributos técnicos como tipo_de_pele, ingredientes, etc.
    """
    if not additional_property:
        return {
            "score": 0,
            "problema": "additionalProperty ausente (campo crítico para agentes)",
            "penalidade": -20
        }
    
    # Conta quantos PropertyValue tem valor preenchido
    if isinstance(additional_property, list):
        preenchidos = [
            prop for prop in additional_property
            if prop.get("value") and len(str(prop.get("value", ""))) > 2
        ]
        
        if len(preenchidos) == 0:
            return {
                "score": 20,
                "problema": "additionalProperty vazio (sem valores preenchidos)",
                "penalidade": -15
            }
        
        if len(preenchidos) < 3:
            return {
                "score": 60,
                "problema": f"additionalProperty com poucos campos ({len(preenchidos)})",
                "penalidade": -5
            }
    
    # additionalProperty OK
    return {
        "score": 100,
        "problema": None,
        "penalidade": 0
    }


def avaliar_schema_quality(schema: dict, structure_score: int) -> dict:
    """
    Avalia qualidade do conteúdo do Schema.org Product.
    
    Args:
        schema: JSON-LD extraído pelo Agente 2
        structure_score: Score estrutural do Agente 2 (0-100)
    
    Returns:
        {
            "structure_score": 84,  # Do Agente 2
            "quality_score": 54,    # Novo — conteúdo útil?
            "problemas": [...],
            "campos_faltando": [...],
            "penalidade_total": -30
        }
    """
    
    problemas = []
    campos_faltando = []
    penalidade_total = 0
    
    # ── Analisa description ──────────────────────────────
    desc = schema.get("description", "")
    analise_desc = analisar_description(desc)
    
    if analise_desc["problema"]:
        problemas.append(analise_desc["problema"])
        penalidade_total += analise_desc["penalidade"]
    
    # ── Analisa additionalProperty ───────────────────────
    additional = schema.get("additionalProperty", [])
    analise_additional = analisar_additional_property(additional)
    
    if analise_additional["problema"]:
        problemas.append(analise_additional["problema"])
        penalidade_total += analise_additional["penalidade"]
    
    # ── Verifica campos essenciais ───────────────────────
    for campo, peso in CAMPOS_ESSENCIAIS.items():
        if campo not in schema or not schema[campo]:
            campos_faltando.append(campo)
            penalidade_total -= peso
    
    # ── Verifica campos desejáveis ───────────────────────
    for campo, peso in CAMPOS_DESEJÁVEIS.items():
        if campo not in schema or not schema[campo]:
            if campo == "additionalProperty":
                # Já foi tratado acima
                continue
            campos_faltando.append(campo)
            penalidade_total -= peso // 2  # Penalidade menor
    
    # ── Calcula quality_score ────────────────────────────
    quality_score = max(0, min(100, structure_score + penalidade_total))
    
    return {
        "agente": "agent2.5_schema_quality",
        "status": "ok",
        "structure_score": structure_score,  # Do Agente 2
        "quality_score": quality_score,      # Novo
        "problemas": problemas,
        "campos_faltando": campos_faltando,
        "penalidade_total": penalidade_total,
        "nota": "Schema existe mas pode ter marketing gloss ou campos vazios"
    }


def run(resultado_agent2: dict) -> dict:
    """
    Interface padrão do orquestrador.
    
    Args:
        resultado_agent2: Output completo do Agente 2 (schema parser)
    
    Returns:
        Análise de qualidade do Schema
    """
    schema = resultado_agent2.get("schema_extraido", {})
    structure_score = resultado_agent2.get("score", 0)
    
    if not schema:
        return {
            "agente": "agent2.5_schema_quality",
            "status": "erro",
            "erro": "Schema não foi extraído pelo Agente 2",
            "structure_score": 0,
            "quality_score": 0
        }
    
    return avaliar_schema_quality(schema, structure_score)


# ─────────────────────────────────────────
# EXECUÇÃO DIRETA (teste manual)
# ─────────────────────────────────────────

if __name__ == "__main__":
    import json
    
    # Simula Schema da Natura (marketing gloss)
    schema_natura = {
        "@type": "Product",
        "name": "Sérum Intensivo Multiclareador Chronos Derma",
        "description": "• menos 84% de manchas* em duas semanas¹ • clareia diferentes tipos de manchas*: sol, acne, envelhecimento, hormonais, gravidez, sardas respeitando o tom natural da pele¹ • 91% pele uniforme imediatamente²",
        "brand": "Natura",
        "offers": {
            "@type": "Offer",
            "price": "89.90"
        }
        # Falta: additionalProperty, ingredients
    }
    
    resultado_agent2_fake = {
        "score": 84,
        "schema_extraido": schema_natura
    }
    
    print("\n🧪 TESTANDO AGENTE 2.5 — SCHEMA QUALITY\n")
    print("Schema de teste: Natura (marketing gloss)\n")
    
    resultado = run(resultado_agent2_fake)
    
    print("=" * 70)
    print(json.dumps(resultado, indent=2, ensure_ascii=False))
    print("=" * 70)
    
    print(f"\n📊 RESUMO:")
    print(f"  Structure Score: {resultado['structure_score']}/100 (Schema existe?)")
    print(f"  Quality Score:   {resultado['quality_score']}/100 (Conteúdo útil?)")
    print(f"  Penalidade:      {resultado['penalidade_total']} pontos")
    print(f"\n⚠️  PROBLEMAS:")
    for p in resultado['problemas']:
        print(f"  • {p}")
