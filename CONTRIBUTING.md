# 👻 Contribuindo com o ghostprod

Obrigada pelo interesse! O ghostprod é um projeto solo por enquanto, mas este guia serve para manter consistência — inclusive para a Eva de daqui a 3 meses que vai esquecer como tudo funciona.

---

## Regras de ouro

```
🚫 NUNCA fazer deploy às sextas-feiras
   Freeze: sexta 17h → segunda 9h

🚫 NUNCA commitar .env ou chaves de API
   Use .env.example com valores fictícios

🚫 NUNCA fazer merge direto em main
   Todo código passa por develop primeiro
```

---

## Fluxo de trabalho

### 1. Para features novas

```bash
git checkout develop
git pull origin develop
git checkout -b feature/nome-da-feature

# ... faz as alterações ...

git add .
git commit -m "feat: descrição curta da feature"
git push origin feature/nome-da-feature

# Abre PR para develop (não para main)
```

### 2. Para correções de bug

```bash
git checkout develop
git checkout -b fix/nome-do-bug

git commit -m "fix: descrição do bug corrigido"
# PR para develop
```

### 3. Para hotfixes urgentes em produção

```bash
git checkout main
git checkout -b hotfix/nome-do-problema

git commit -m "hotfix: descrição"
# PR para main E para develop
```

---

## Convenção de commits

```
feat:     nova funcionalidade
fix:      correção de bug
docs:     mudança em documentação
style:    formatação (sem mudança de lógica)
refactor: refatoração sem nova feature ou fix
test:     adição ou correção de testes
chore:    tarefas de manutenção (deps, config)

Exemplos:
feat: adiciona Agente 4 com Claude API
fix: corrige timeout do Playwright no Boticário
docs: atualiza score-calculation.md com novos pesos
test: adiciona teste de rate limiting por IP
```

---

## Definition of Done

Antes de abrir PR, confirma que:

- [ ] Código roda localmente sem erros
- [ ] Testes unitários passando (`pytest tests/ -v`)
- [ ] Sem chaves de API no código ou nos commits
- [ ] `.env.example` atualizado se adicionou nova variável
- [ ] `README.md` atualizado se mudou a interface pública
- [ ] Sem `console.log` de debug esquecido no frontend

---

## Estrutura dos testes

```bash
# Roda tudo
pytest backend/tests/ -v

# Roda só um agente
pytest backend/tests/test_agent2_schema.py -v

# Com cobertura
pytest backend/tests/ --cov=backend --cov-report=term-missing

# Teste E2E (requer Playwright instalado)
pytest backend/tests/test_e2e.py -v
```

---

## Adicionando uma nova variável de ambiente

1. Adiciona no `.env` local (nunca commita)
2. Adiciona no `.env.example` com valor fictício
3. Documenta em `docs/api.md`
4. Adiciona como GitHub Secret se necessário para CI/CD

---

## Dúvidas?

Abre uma issue ou manda mensagem: [ghostprod.io](https://ghostprod.io)
