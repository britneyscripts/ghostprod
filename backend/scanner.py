import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import json
import time

# ─────────────────────────────────────────
# PARTE 1: requests + BeautifulSoup
# O jeito simples — não renderiza JavaScript
# ─────────────────────────────────────────

def scan_simples(url):
    """
    Faz uma requisição HTTP simples.
    Recebe só o HTML estático — sem esperar JS rodar.
    É o que a maioria dos scripts de scraping faz.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (compatible; AgenticAudit/1.0)'
    }
    
    inicio = time.time()
    response = requests.get(url, headers=headers, timeout=10)
    tempo = round((time.time() - inicio) * 1000)  # em milissegundos
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Procura por Schema.org no HTML estático
    schemas = soup.find_all('script', type='application/ld+json')
    dados_estruturados = []
    for s in schemas:
        try:
            dados_estruturados.append(json.loads(s.string))
        except:
            continue
    
    tem_produto = any(
        d.get('@type') == 'Product' 
        for d in dados_estruturados
    )
    
    return {
        "metodo": "requests + BeautifulSoup",
        "tempo_ms": tempo,
        "schemas_encontrados": len(dados_estruturados),
        "tem_schema_produto": tem_produto,
        "dados_brutos": dados_estruturados
    }


# ─────────────────────────────────────────
# PARTE 2: Playwright
# Abre browser real, executa JavaScript,
# devolve HTML completo — como um agente veria
# ─────────────────────────────────────────

def scan_playwright(url):
    """
    Abre Chromium headless (sem janela visível).
    Espera o JavaScript executar completamente.
    Captura o HTML após renderização.
    Mede o tempo que isso levou.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        inicio = time.time()
        
        # Navega e espera a rede estabilizar
        # "networkidle" = espera não haver mais requisições por 500ms
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(3000)
        
        tempo = round((time.time() - inicio) * 1000)  # em milissegundos
        
        
        # Pega o HTML completo já renderizado
        html = page.content()
        browser.close()
    
    # Agora parseia com BeautifulSoup — mas no HTML completo
    soup = BeautifulSoup(html, 'html.parser')
    
    schemas = soup.find_all('script', type='application/ld+json')
    dados_estruturados = []
    for s in schemas:
        try:
            dados_estruturados.append(json.loads(s.string))
        except:
            continue
    
    # Extrai campos específicos do Schema de Produto
    produto_info = {}
    for d in dados_estruturados:
        if d.get('@type') == 'Product':
            produto_info = {
                "nome": d.get('name', 'ausente'),
                "preco": d.get('offers', {}).get('price', 'ausente'),
                "disponibilidade": d.get('offers', {}).get('availability', 'ausente'),
                "rating": d.get('aggregateRating', {}).get('ratingValue', 'ausente'),
                "total_reviews": d.get('aggregateRating', {}).get('reviewCount', 'ausente'),
                "descricao": d.get('description', 'ausente')[:100] if d.get('description') else 'ausente'
            }
    
    tem_produto = any(
        d.get('@type') == 'Product' 
        for d in dados_estruturados
    )
    
    return {
        "metodo": "Playwright (browser real)",
        "tempo_ms": tempo,
        "schemas_encontrados": len(dados_estruturados),
        "tem_schema_produto": tem_produto,
        "produto_info": produto_info,
        "dados_brutos": dados_estruturados
    }


# ─────────────────────────────────────────
# EXECUÇÃO — compara os dois métodos
# ─────────────────────────────────────────

def comparar(url, nome_site):
    print(f"\n{'='*60}")
    print(f"SITE: {nome_site}")
    print(f"URL: {url[:60]}...")
    print(f"{'='*60}")
    
    print("\n→ Método 1: requests simples...")
    resultado_simples = scan_simples(url)
    print(f"  Tempo: {resultado_simples['tempo_ms']}ms")
    print(f"  Schemas encontrados: {resultado_simples['schemas_encontrados']}")
    print(f"  Tem Schema de Produto: {resultado_simples['tem_schema_produto']}")
    
    print("\n→ Método 2: Playwright (browser real)...")
    resultado_playwright = scan_playwright(url)
    print(f"  Tempo: {resultado_playwright['tempo_ms']}ms")
    print(f"  Schemas encontrados: {resultado_playwright['schemas_encontrados']}")
    print(f"  Tem Schema de Produto: {resultado_playwright['tem_schema_produto']}")
    
    if resultado_playwright['produto_info']:
        print("\n  Dados do Produto encontrados:")
        for campo, valor in resultado_playwright['produto_info'].items():
            print(f"    {campo}: {valor}")
    else:
        print("\n  Nenhum dado de produto estruturado encontrado.")


# ─────────────────────────────────────────
# RODA OS DOIS SITES
# ─────────────────────────────────────────

URL_BOTICARIO = "https://www.boticario.com.br/serum-de-alta-potencia-vitamina-c-10-botik-30ml-v2/?sku=B51467"
URL_NATURA    = "https://www.natura.com.br/p/serum-intensivo-lifting-e-firmeza-chronos-derma-30-ml/NATBRA-169247"

comparar(URL_BOTICARIO, "O Boticário")
comparar(URL_NATURA, "Natura")






