# 🚀 Deploy no Vercel

## Preparação para Vercel

Este projeto foi preparado para ser hospedado no **Vercel** usando a arquitetura serverless.

### ✅ Requisitos

- Conta no [Vercel](https://vercel.com)
- Banco de dados PostgreSQL rodando (recomendado: [Neon](https://neon.tech))
- Git/GitHub configurado

### 📋 Passos para Deploy

#### 1. Preparar o Banco de Dados

1. Sinal até no [Neon.tech](https://neon.tech) (PostgreSQL serverless)
2. Crie um novo projeto e copie a **DATABASE_URL**
3. Execute o schema do projeto:
   ```bash
   psql "your_database_url" < schema.sql
   ```

#### 2. Configurar Variáveis de Ambiente no Vercel

1. Acesse o painel do Vercel
2. Vá em **Settings** → **Environment Variables**
3. Adicione as variáveis do arquivo `.env.example`:

```
DATABASE_URL=postgresql://...
FLASK_ENV=production
FLASK_DEBUG=0
```

#### 3. Conectar Repositório Git

1. Faça push do projeto para GitHub
2. No Vercel, clique em **New Project**
3. Selecione o repositório
4. Vercel detectará automaticamente que é um projeto Python
5. Clique em **Deploy**

#### 4. Verificar Deploy

Após o deploy, teste os endpoints:

```bash
curl https://seu-projeto.vercel.app/api/profissionais
curl https://seu-projeto.vercel.app/api/health
```

### 🌐 URLs Importantes

- **API Base:** `https://seu-projeto.vercel.app/api`
- **Frontend:** `https://seu-projeto.vercel.app`
- **Status:** `https://seu-projeto.vercel.app/api/health`

### 📊 Estrutura para Vercel

```
agenda_app/
├── api/
│   └── index.py          # Entry point (Vercel)
├── templates/
│   └── index.html        # Frontend
├── vercel.json           # Configuração Vercel
├── requirements.txt      # Dependências Python
├── .env.example          # Variáveis exemplo
├── app.py                # App Flask main
├── database.py           # Modelos SQLAlchemy
├── agenda_manager_db.py  # Lógica de negócio
└── ...
```

### 🔧 Configuração Detalhada

O arquivo `vercel.json` especifica:

- **Python 3.11** como runtime
- **Build automático** do ambiente
- **Roteamento** de requisições para `api/index.py`
- **Limite máximo** de 50MB para cada serverless function

### ⚠️ Limitações do Vercel (Serverless)

1. **Timeout:** Máximo 60 segundos por requisição
2. **Armazenamento:** Sem armazenamento persistente na função (use banco de dados)
3. **Conexões:** Certifique-se que o PostgreSQL aceita conexões externas
4. **Cold Start:** Primeira requisição pode levar alguns segundos

### 🔒 Segurança

- Nunca faça commit do `.env` (já está em `.gitignore`)
- Use `.env.example` como template
- Adicione variables no painel do Vercel, não em código

### 🛠️ Troubleshooting

**Erro: "No module named 'database'"**
- Certifique-se que todos os imports estão relativos ao caminho correto
- O `api/index.py` adiciona o diretório pai ao `sys.path`

**Erro: "DATABASE_URL not found"**
- Adicione `DATABASE_URL` nas variáveis de ambiente do Vercel

**Timeout em operações**
- PostgreSQL pode estar lento do Neon
- Verifique a conexão do banco

**CORS errors**
- Adicione sua domain em `CORS_ORIGINS` (ou deixe `*` para aceitar todas)

### 📚 Recursos Úteis

- [Vercel Python Docs](https://vercel.com/docs/functions/python)
- [Neon PostgreSQL](https://neon.tech)
- [Flask on Vercel](https://flask.palletsprojects.com/)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org/)

### 🚢 Próximas Etapas

Após o primeiro deploy:

1. Teste a API com seus endpoints
2. Configure um domínio customizado no Vercel
3. Configure HTTPS (automático)
4. Implemente CI/CD automático

---

**Dúvidas?** Consulte a documentação do Vercel ou arquivo README.md principal.
