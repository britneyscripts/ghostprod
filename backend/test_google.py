import requests
import os
from dotenv import load_dotenv

load_dotenv()
chave = os.getenv("PSI_API_KEY")

print("Chave carregada:", "Sim" if chave else "Não")

url_api = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
params = {
    "url": "https://www.google.com.br",  # Mudamos para o Google só para validar a chave!
    "strategy": "MOBILE",
    "category": "performance",
    "key": chave
}

print("Chamando a API... (Aguarde no máximo 15 segundos)")

try:
    # Colocamos um limite de 15 segundos
    resposta = requests.get(url_api, params=params, timeout=15)
    
    print("\n--- RESPOSTA DO GOOGLE ---")
    print("STATUS:", resposta.status_code)
    
    if resposta.status_code == 400:
        print("MOTIVO EXATO DO ERRO:", resposta.text)
    elif resposta.status_code == 200:
        print("🎉 SUCESSO ABSOLUTO! A sua chave está funcionando perfeitamente.")
    else:
        print("OUTRO STATUS:", resposta.text)

except requests.exceptions.Timeout:
    print("⏳ ERRO: O Google demorou mais de 15 segundos e desistimos.")
except Exception as e:
    print("🔥 ERRO DESCONHECIDO:", str(e))