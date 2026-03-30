# Plano de Migração — Público → Privado

## O que sai PERMANENTEMENTE do repo público

Execute na ordem abaixo. Cada comando remove do histórico do git E do disco.

---

### PASSO 1 — Copiar tudo para o repo privado ANTES de apagar

```bash
# Cria a pasta do repo privado (fora do ghostproduct)
mkdir ~/ghostprod-core
cd ~/ghostprod-core
git init
git branch -M main

# Copia os arquivos que vão para o privado
cp -r ~/ghostproduct/backend .
cp ~/ghostproduct/firebase-blueprint.json .
cp ~/ghostproduct/.env.example .
cp ~/ghostproduct/.gitignore .

# Estrutura de pastas para pesquisa
mkdir -p data/raw data/processed notebooks docs/specs tcc

# Primeiro commit
git add .
git commit -m "init: backend + research data migrado do repo público"
```

---

### PASSO 2 — Criar repo privado no GitHub

1. Acesse: https://github.com/new
2. Nome: `ghostprod-core`
3. Visibilidade: **Private** ← obrigatório
4. NÃO inicializar com README (já temos)

```bash
cd ~/ghostprod-core
git remote add origin https://github.com/britneyscripts/ghostprod-core.git
git push -u origin main
```

---

### PASSO 3 — Remover backend do repo público

```bash
cd ~/ghostproduct

# Remove o diretório backend do git tracking
git rm -r --cached backend/
git rm --cached firebase-blueprint.json

# Remove fisicamente (você já tem a cópia no privado)
rm -rf backend/
rm firebase-blueprint.json
```

---

### PASSO 4 — Atualizar .gitignore do repo público

Adicionar ao .gitignore do repo público para garantir que não volta:

```
# Nunca volta para o repo público
backend/
firebase-blueprint.json
data/
notebooks/
tcc/
*.ipynb
```

---

### PASSO 5 — Commit e push

```bash
cd ~/ghostproduct

git add .gitignore README.md
git commit -m "chore: backend movido para repo privado ghostprod-core

- Remove backend/ do repo público (IP protegido)
- Remove firebase-blueprint.json (arquitetura interna)
- Atualiza README para público CPO/diretores
- Backend agora em repositório privado separado"

git push origin main
```

---

## O que FICA no repo público

```
ghostprod/ (público — britneyscripts/ghostprod)
├── frontend/              ✅ FICA — mostra skill técnica de PM
│   └── src/
│       ├── App.tsx        ✅ FICA — UI vaporwave (portfólio)
│       ├── firebase.ts    ✅ FICA — integração (sem credenciais)
│       └── index.css      ✅ FICA — design system
├── docs/                  ✅ FICA — market analysis (a ser populado)
├── README.md              ✅ FICA — posicionamento para CPO/diretores
├── CONTRIBUTING.md        ✅ FICA
├── LICENSE                ✅ FICA
├── .gitignore             ✅ FICA
├── .env.example           ✅ FICA — só nomes de variáveis, sem valores
└── firestore.rules        ✅ FICA — regras de segurança (sem IP)
```

---

## O que VAI para o repo privado

```
ghostprod-core/ (privado — britneyscripts/ghostprod-core)
├── backend/
│   ├── main.py                ← FastAPI app
│   ├── scanner.py             ← pipeline principal ← IP
│   ├── orchestrator.py        ← lógica de orquestração ← IP
│   ├── crux_pipeline.py       ← extração CrUX ← IP
│   ├── requirements.txt
│   └── agents/
│       ├── agent1_crux.py     ← Performance agent ← IP
│       ├── agent1_pagespeed.py
│       ├── agent2_schema.py   ← Schema agent ← IP
│       ├── agent2_5_schema_quality.py ← IP
│       ├── agent3_nlp.py      ← NLP agent ← IP
│       └── agent4_gap.py      ← Gap analysis agent ← IP
├── firebase-blueprint.json    ← arquitetura interna
├── data/
│   ├── raw/                   ← coletas diárias (a criar)
│   └── processed/             ← datasets TCC (a criar)
├── notebooks/                 ← análise exploratória (a criar)
├── docs/specs/                ← specs SDD (a criar)
└── tcc/                       ← capítulos em rascunho (a criar)
```

---

## Verificação final

Após a migração, verificar:

```bash
# No repo PÚBLICO — não deve aparecer backend/
cd ~/ghostproduct
git ls-files | grep backend   # deve retornar vazio

# No repo PRIVADO — deve ter tudo
cd ~/ghostprod-core
git ls-files | grep agent     # deve listar os 4 agentes

# Confirmar que .gitignore bloqueia backend no público
echo "backend/test.txt" > backend/test.txt 2>/dev/null || mkdir -p backend && echo "test" > backend/test.txt
git status  # backend/ NÃO deve aparecer como untracked
rm -rf backend/test.txt
```

---

## O que isso comunica externamente

**Repo público (CPO/diretores veem):**
- Frontend bem construído com design system próprio
- README posicionando a pesquisa e o produto
- Nenhum detalhe de implementação do algoritmo

**Repo privado (só você):**
- Todo o IP: agentes, fórmula, dados coletados
- TCC em desenvolvimento
- Análises e notebooks

*A separação é o posicionamento: você mostra que sabe construir (frontend público) sem revelar o diferencial competitivo (backend privado).*
