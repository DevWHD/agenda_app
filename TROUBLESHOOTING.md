# 🔧 Troubleshooting - Erros Intermitentes

## Problemas Corrigidos

Este documento lista os problemas que causavam erros intermitentes ao carregar dados e como foram resolvidos.

---

## 🐛 Problema 1: Falta de Tratamento de Erro em Conexão com Banco

### Sintoma
```
OperationalError: connection timeout
sqlalchemy.exc.DatabaseError
```

### Causa
- A aplicação não tinha retry logic em caso de falha de conexão
- Pool de conexões não estava configurado adequadamente
- Sem timeout adequado nas operações do banco

### Solução
✅ **database.py:**
- Adicionado `pool_timeout=30` para timeout ao obter conexão
- Configurado keep-alive para manter conexões vivas
- Adicionada função `verificar_conexao_banco()` para checar saúde da conexão
- Adicionada função `executar_com_retry()` com retry exponencial

✅ **agenda_manager_db.py:**
- Adicionar decorator `@com_retry` em todos os métodos que acessam banco de dados
- Implementado retry logic com backoff exponencial (2^tentativa)
- Logging mais detalhado de erros

---

## 🐛 Problema 2: Tratamento de Erro Insuficiente nos Endpoints API

### Sintoma
```json
{
  "erro": "Internal Server Error",
  "status": 500
}
```

### Causa
- Endpoints não tinham try-catch adequado
- Erros de banco passavam sem tratamento
- Sem fallback quando sistema não estava inicializado

### Solução
✅ **app.py:**
- Adicionado try-catch em TODOS os endpoints
- Inicialização segura de `AgendaManagerDB` com verificação
- Validação se `agenda` existe antes de usar
- Tratamento específico para diferentes tipos de erro (400, 404, 503, 500)
- Erro handler global para 404 e 500

---

## 🐛 Problema 3: Health Check Faltando

### Sintoma
- Sem forma de verificar se a API estava saudável
- Sem indicação se banco de dados estava conectado

### Causa
- Sem endpoint de health check
- Sem monitoramento de status do sistema

### Solução
✅ Adicionado novo endpoint: **GET /api/health**
```bash
curl http://localhost:5001/api/health
```

Retorna:
```json
{
  "status": "ok",
  "database": "connected",
  "timestamp": "2026-02-11T10:30:00.123456"
}
```

---

## 🐛 Problema 4: Cache Falhando Silenciosamente

### Sintoma
- Dados não aparecerem quando cache estava cheio
- Sem erro quando cache falha

### Causa
- Cache sem tratamento de erro
- Endpoint tinha fallback para banco mas sem verificação

### Solução
✅ **app.py:**
- Cache com fallback automático para banco se vazio
- Limpeza de cache após criar/cancelar agendamento
- Cache separado por tipo de dado (profissionais, procedimentos, dashboard)

---

## 🐛 Problema 5: Validação de Parâmetros Fraca

### Sintoma
```
ValueError: invalid literal for int()
TypeError: unsupported operand type(s)
```

### Causa
- Parâmetros não validados antes de usar
- Conversão de tipo sem tratamento
- Parâmetros obrigatórios não verificados

### Solução
✅ **app.py:**
- Validação de parâmetros em todos os endpoints
- Conversão segura de tipos (try-except)
- Mensagens de erro específicas para cada campo obrigatório
- Antes-request hook para validar Content-Type

---

## 🐛 Problema 6: Bare `except` Ocultando Erros

### Sintoma
```python
except:
    return False  # Qual erro aconteceu?
```

### Causa
- Uso de bare `except` que captura TODOS os erros
- Sem logging do erro real
- Difícil debug

### Solução
✅ **agenda_manager_db.py:**
- Removido bare `except` 
- Usar específicos: `except ValueError:`, `except Exception:`
- Sempre logar o erro com `logger.error(f"Erro: {e}")`
- Levar o erro adiante com `raise`

---

## 📋 Checklist de Estabilidade

Use isso para verificar se sistema está saudável:

```bash
# 1. Verificar saúde
curl http://localhost:5001/api/health

# 2. Listar profissionais
curl http://localhost:5001/api/profissionais

# 3. Ver datas disponíveis
curl http://localhost:5001/api/profissionais/1/datas-disponiveis

# 4. Verificar horários
curl "http://localhost:5001/api/profissionais/1/horarios?data=20/02/2026&procedimento_id=101"

# 5. Teste de agendamento
curl -X POST http://localhost:5001/api/agendamentos \
  -H "Content-Type: application/json" \
  -d '{
    "profissional_id": 1,
    "data": "20/02/2026",
    "hora": "10:00",
    "cliente_nome": "Teste",
    "cliente_telefone": "11999999999",
    "procedimento_id": 101,
    "procedimento_nome": "Teste"
  }'
```

---

## 🔍 Como Debugar Erros

### 1. Ver Logs em Tempo Real
```bash
# Durante execução local
python app.py

# Ou com mais detalhes
FLASK_ENV=development python app.py
```

### 2. Verificar Banco de Dados
```bash
# Conectar ao PostgreSQL
psql $DATABASE_URL

# Ver tabelas
\dt

# Ver agendamentos
SELECT * FROM agendamentos;
```

### 3. Usar Health Check
```bash
# Verificar saúde do sistema
while true; do
  curl -s http://localhost:5001/api/health | jq .
  sleep 5
done
```

### 4. Aumentar Logging
Em `app.py`, mude:
```python
logging.basicConfig(level=logging.DEBUG)  # Mais verboso
```

---

## ⚠️ Possíveis Causas Restantes

Se ainda houver erros intermitentes:

1. **Conexão de Rede**
   - Ping do PostgreSQL: `ping sua_database.neon.tech`
   - Testar com tools como `psql` ou `pgAdmin`

2. **Pool de Conexões Esgotado**
   - Aumentar `pool_size` e `max_overflow` em `database.py`
   - Monitorar uso de conexões

3. **Query Lenta**
   - Adicionar índices ao banco (veja schema.sql)
   - Usar `EXPLAIN ANALYZE` para verificar plano de execução

4. **Timeout CORS**
   - Verificar configuração de CORS
   - Se usando Vercel, pode ser timeout de 60s

5. **Variáveis de Ambiente**
   - `DATABASE_URL` não está definida
   - Executar `echo $DATABASE_URL` para verificar

---

## 📞 Próximos Passos

1. **Teste Completo**: Execute todos os endpoints do checklist
2. **Monitor**: Implemente monitoramento (Sentry, Datadog, etc)
3. **Logs**: Configure agregação de logs (ELK, CloudWatch, etc)
4. **Alertas**: Configure alertas para erros críticos
5. **Backup**: Faça backup regular do PostgreSQL

---

**Data:** Fevereiro 2026  
**Versão:** 1.0 (após correções de estabilidade)
