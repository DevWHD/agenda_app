# 📋 Checklist de Deployment

Use este checklist antes de fazer deploy do projeto em qualquer plataforma.

## ✅ Pré-Deployment

- [ ] All código foi testado localmente
- [ ] Não há variáveis sensíveis no código (use `.env`)
- [ ] `.env.local` ou `.env` **NÃO foi** commitado no git
- [ ] Todos os arquivos necessários estão no repositório
- [ ] `requirements.txt` está atualizado com todas as dependências
- [ ] PostgreSQL está rodando e acessível
- [ ] Database schema foi criado (execute `setup_db.py`)

## 🔐 Segurança

- [ ] `DATABASE_URL` está segura nas secrets do Vercel
- [ ] Senhas e tokens não estão em código aberto
- [ ] CORS está configurado para domínios específicos (não genérico `*`)
- [ ] Flask `DEBUG` está `False` em produção
- [ ] `SECRET_KEY` da Flask está segura

## 📦 Vercel Specifico

- [ ] `vercel.json` está configurado corretamente
- [ ] `api/index.py` existe e exporta a app Flask
- [ ] `requirements.txt` contém `gunicorn` (necessário para Vercel)
- [ ] `runtime.txt` especifica a versão correta do Python
- [ ] Variáveis de ambiente estão adicionadas no painel Vercel

## 🗄️ Banco de Dados

- [ ] PostgreSQL está acessível de fora (se usando Neon ou similar)
- [ ] Connection string (`DATABASE_URL`) está correta
- [ ] Todas as tabelas foram criadas
- [ ] Dados iniciais foram inseridos (se necessário)
- [ ] Backup foi feito antes do deploy

## 🌐 Configuração DNS

- [ ] Domínio foi configurado (se usandocustomizado)
- [ ] HTTPS está habilitado
- [ ] DNS registra corretamente

## 🧪 Testes Pós-Deployment

- [ ] API está respondendo no novo domínio
- [ ] Endpoints `/api/profissionais` retorna dados
- [ ] `/api/health` retorna status OK
- [ ] Templates HTML carregam corretamente
- [ ] Erros 4xx e 5xx retornam JSON apropriado
- [ ] Static files (CSS, JS) carregam corretamente

## 📊 Monitoramento

- [ ] Configure logging no Vercel
- [ ] Faça testes de carga básicos
- [ ] Monitore perfomance e timeouts
- [ ] Configure alertas para erros críticos

## 🔄 CI/CD (se usando GitHub Actions)

- [ ] Arquivo `.github/workflows/deploy.yml` está configurado
- [ ] Secrets do Vercel foram adicionados no GitHub:
  - [ ] `VERCEL_TOKEN`
  - [ ] `VERCEL_ORG_ID`
  - [ ] `VERCEL_PROJECT_ID`
- [ ] Workflow executa sem erros

## 🆘 Troubleshooting

Se algo der errado:

1. **Erro 500:** Verifique logs do Vercel (`vercel logs`)
2. **Módulo não encontrado:** Certifique-se que está em `requirements.txt`
3. **Database connection:** Verifique `DATABASE_URL` nas variáveis
4. **Timeout:** Aumente timeout na `vercel.json` ou otimize queries
5. **Import errors:** Verifique caminhos relativos no `api/index.py`

## 📚 Documentação

- Verifique [VERCEL_DEPLOY.md](./VERCEL_DEPLOY.md)
- Consulte [README.md](./README.md)
- Leia [QUICK_START.md](./QUICK_START.md)

---

**Última atualização:** Fevereiro 2026
