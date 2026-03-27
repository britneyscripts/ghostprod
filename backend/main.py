"""
ghostprod — main.py
─────────────────────────────────────────────────────────
FastAPI — endpoint principal /analyze.

Uso:
    uvicorn main:app --reload --port 8000

Endpoints:
    POST /analyze       — analisa uma URL
    GET  /health        — status do servidor
"""

import os
import time
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from dotenv import load_dotenv

from orchestrator import analisar

load_dotenv()

app = FastAPI(
    title="ghostprod API",
    description="Agent-Readiness Score para PDPs de e-commerce",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Isso permite que o seu Frontend (porta 3000) fale com o Backend (8000)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# CORS — permite o frontend chamar o backend
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Rate limiting simples em memória ─────────────────────
# Para produção: migrar para Redis ou Firestore
_contador_ip: dict = {}
_contador_mensal: dict = {"total": 0}

RATE_LIMIT_PER_IP = int(os.getenv("RATE_LIMIT_PER_IP", 10))
RATE_LIMIT_MONTHLY = int(os.getenv("RATE_LIMIT_MONTHLY", 500))


def check_rate_limit(ip: str):
    """Verifica limites de uso."""
    # Limite mensal global
    if _contador_mensal["total"] >= RATE_LIMIT_MONTHLY:
        raise HTTPException(
            status_code=429,
            detail=f"Limite mensal de {RATE_LIMIT_MONTHLY} análises atingido. "
                   "Contate ghostprod.io para acesso beta."
        )

    # Limite por IP
    hoje = time.strftime("%Y-%m-%d")
    chave = f"{ip}:{hoje}"
    _contador_ip[chave] = _contador_ip.get(chave, 0) + 1

    if _contador_ip[chave] > RATE_LIMIT_PER_IP:
        raise HTTPException(
            status_code=429,
            detail=f"Limite de {RATE_LIMIT_PER_IP} análises por dia por IP atingido."
        )

    _contador_mensal["total"] += 1


# ── Modelos ───────────────────────────────────────────────

class AnalyzeRequest(BaseModel):
    url: str
    query: str = None  # query opcional para o Gap Analysis


class AnalyzeResponse(BaseModel):
    url: str
    ars: int
    classificacao: dict
    agentes: dict
    recomendacoes: list
    pesos_utilizados: dict
    nota: str


# ── Endpoints ─────────────────────────────────────────────

@app.get("/health")
def health():
    return {
        "status": "ok",
        "versao": "0.1.0",
        "analises_realizadas": _contador_mensal["total"],
        "limite_mensal": RATE_LIMIT_MONTHLY
    }


@app.post("/analyze")
def analyze(request_data: AnalyzeRequest, request: Request):
    """
    Analisa uma PDP e retorna o Agent-Readiness Score.
    """
    ip = request.client.host
    check_rate_limit(ip)

    url = str(request_data.url)

    # Validação básica — só aceita e-commerces brasileiros na v0.1
    dominios_br = [
        "natura.com.br", "boticario.com.br", "sephora.com.br",
        "belezanaweb.com.br", "americanas.com.br", "magazineluiza.com.br",
        "mercadolivre.com.br", "shopee.com.br", "amazon.com.br",
        "carrefour.com.br", "extra.com.br", "casasbahia.com.br",
        "netshoes.com.br", "centauro.com.br", "dafiti.com.br",
    ]

    # Em v0.1 — aceita qualquer URL mas avisa se não for BR
    is_br = any(dominio in url for dominio in dominios_br)

    try:
        resultado = analisar(url, query=request_data.query)
        if not is_br:
            resultado["aviso"] = (
                "ghostprod é otimizado para e-commerces brasileiros. "
                "Esta URL pode ter dados CrUX limitados."
            )
        return resultado

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro na análise: {str(e)}"
        )
