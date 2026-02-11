# 🚀 Guia de Deployment

Este projeto está preparado para ser hospedado em múltiplas plataformas. Escolha a que melhor se adequa suas necessidades.

## 📊 Comparação de Plataformas

| Plataforma | Setup | Custo | Performance | Ideal Para |
|-----------|-------|-------|-------------|-----------|
| **Vercel** | ⭐⭐⭐ Fácil | Gratuito | Muito Rápido | Serverless, escalabilidade |
| **Heroku** | ⭐⭐ Médio | Pago | Rápido | Apps pequenas/médias |
| **Docker** | ⭐⭐⭐⭐ Complexo | Variável | Rápido | Full control, containerização |
| **Railway** | ⭐⭐⭐ Fácil | Gratuito | Muito Rápido | Alternativa ao Heroku |
| **Render** | ⭐⭐⭐ Fácil | Gratuito | Rápido | Apps Python simples |

---

## 1️⃣ VERCEL (Recomendado para Serverless)

### ✨ Vantagens
- Deployment ultra-rápido
- Gratuito para começar
- Zero config (quase)
- Escalabilidade automática
- Integração GitHub perfeita

### ⚠️ Limitações
- Timeout: 60 segundos
- Sem armazenamento persistente
- Cold starts iniciais

### 🚀 Como Fazer Deploy
1. Siga [VERCEL_DEPLOY.md](./VERCEL_DEPLOY.md)
2. Arquivos necessários já estão criados:
   - `vercel.json` - Configuração
   - `api/index.py` - Entry point
   - `runtime.txt` - Versão Python

---

## 2️⃣ HEROKU

### ✨ Vantagens
- Muito simples de usar
- Dyno sempre ligado (com custo)
- Suporte excelente

### ⚠️ Limitações
- Não tem free tier mais
- Cold starts (sleep apps)
- Mais caro em longo prazo

### 🚀 Como Fazer Deploy
```bash
# 1. Instale Heroku CLI
# https://devcenter.heroku.com/articles/heroku-cli

# 2. Login
heroku login

# 3. Crie app
heroku create seu-app-name

# 4. Defina variáveis
heroku config:set DATABASE_URL=postgresql://...

# 5. Deploy
git push heroku main
```

Arquivo `Procfile` já está configurado.

---

## 3️⃣ DOCKER (Controle Total)

### ✨ Vantagens
- Máximo controle
- Funciona em qualquer lugar
- Perfetto para CI/CD
- Ambiete isolado

### ⚠️ Limitações
- Mais complexo
- Mais recursos necessários
- Requer conhecimento Docker

### 🚀 Como Fazer Deploy Localmente
```bash
# 1. Build a imagem
docker-compose build

# 2. Inicie os serviços
docker-compose up

# 3. Acesse
http://localhost:5001
```

Arquivos Docker já estão configurados:
- `Dockerfile`
- `docker-compose.yml`
- `.dockerignore`

### Deploy em Plataforma Docker
- **AWS ECS**
- **Google Cloud Run**
- **DigitalOcean App Platform**

---

## 4️⃣ RAILWAY

### ✨ Vantagens
- Muito simples
- Gratuito inicialmente
- GitHub integration automática
- Melhor que Heroku free

### 🚀 Como Fazer Deploy
1. Acesse https://railway.app
2. Login com GitHub
3. New Project → Import from GitHub
4. Selecione seu repositório
5. Configure `DATABASE_URL`
6. Deploy!

---

## 5️⃣ RENDER

### ✨ Vantagens
- Simples e moderno
- Gratuito com creditos iniciais
- Otimizado para Python

### 🚀 Como Fazer Deploy
1. Acesse https://render.com
2. New → Web Service
3. Connect GitHub
4. Selecione repositório
5. Configure ambiente (`DATABASE_URL`)
6. Deploy automático!

---

## 📋 Pre-Deployment Checklist

Antes de qualquer deploy, veja [DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md)

---

## 🔧 Configuração de Banco de Dados

### Neon PostgreSQL (Recomendado)
```
1. Acesse https://neon.tech
2. Crie conta gratuita
3. New Project → Copie DATABASE_URL
4. Define como variável de ambiente
```

### Alternativas
- **Supabase** - PostgeSQL com extras
- **Azure Database** - Enterprise
- **AWS RDS** - Escalável
- **Heroku Postgres** - Integrada (paga)

---

## 🔐 Variáveis de Ambiente Required

```
DATABASE_URL=postgresql://user:password@host/db
FLASK_ENV=production
FLASK_DEBUG=0
```

Opcional:
```
WHATSAPP_API_KEY=...
CORS_ORIGINS=https://seu-dominio.com
```

---

## 📊 Monitoring & Logs

### Vercel
```bash
vercel logs seu-projeto
```

### Heroku
```bash
heroku logs --tail
```

### Docker
```bash
docker logs agenda_app
```

---

## 🆘 Troubleshooting Comum

### "ModuleNotFoundError"
- Verifique `requirements.txt`
- Execute `pip install -r requirements.txt`

### "DATABASE_URL connection failed"
- Teste: `psql $DATABASE_URL`
- Verifique IP whitelist (se usando Neon/Supabase)

### "Import from parent directory"
- Verifique `api/index.py` adiciona parent ao sys.path

### "Timeout (>60s)"
- Vercel tem limite de 60s
- Optimize queries ou use background tasks

---

## 📞 Suporte

- **Vercel Docs:** https://vercel.com/docs
- **Flask Docs:** https://flask.palletsprojects.com/
- **PostgreSQL Docs:** https://www.postgresql.org/docs/
- **SQLAlchemy Docs:** https://docs.sqlalchemy.org/

---

**Último Update:** Fevereiro 2026
