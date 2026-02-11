# ⚡ Quick Start - Agenda App

## 🏃 Começar em 2 Minutos

### 1. Instalar e Executar
```bash
cd c:\Users\Whendel\Documents\agenda_app
python app.py
```

### 2. Acessar no Navegador
```
http://localhost:5001
```

### 3. Testar a API (em outro terminal)
```bash
cd c:\Users\Whendel\Documents\agenda_app
python test_api.py
```

---

## 📋 O que é Agenda App?

- **Tipo:** API REST + Interface Web
- **Framework:** Flask (Python)
- **Porta:** 5001
- **Função:** Gerenciar agendamentos de 3 profissionais
- **Dados:** JSON (config.json)

---

## 🎯 3 Profissionais Inclusos

### 1. 💇‍♀️ Rayssa
- ID: 1
- Especialidade: Corte e Penteado
- Procedimentos: Corte simples, Corte progressiva, Escova, etc.

### 2. 💅 Marcia
- ID: 2
- Especialidade: Manicure/Pedicure
- Procedimentos: Manicure, Pedicure, Alongamento, etc.

### 3. 💇‍♀️ Mirian
- ID: 3
- Especialidade: Cabelo
- Procedimentos: Hidratação, Botox, Progressiva, etc.

---

## 🔌 Principais Endpoints

### Listar Profissionais
```bash
curl http://localhost:5001/api/profissionais
```

### Ver Datas Disponíveis
```bash
curl http://localhost:5001/api/profissionais/1/datas-disponiveis
```

### Ver Horários de um Dia
```bash
curl "http://localhost:5001/api/profissionais/1/horarios?data=20/02/2026&procedimento_id=101"
```

### Criar Agendamento
```bash
curl -X POST http://localhost:5001/api/agendamentos \
  -H "Content-Type: application/json" \
  -d '{
    "profissional_id": 1,
    "data": "20/02/2026",
    "hora": "10:00",
    "cliente_nome": "João Silva",
    "cliente_telefone": "11999999999",
    "procedimento_id": 101,
    "procedimento_nome": "Corte simples"
  }'
```

### Listar Agendamentos de um Profissional
```bash
curl http://localhost:5001/api/profissionais/1/agendamentos
```

### Cancelar Agendamento
```bash
curl -X DELETE http://localhost:5001/api/agendamentos/ID_DO_AGENDAMENTO
```

### Dashboard
```bash
curl http://localhost:5001/api/dashboard
```

---

## 📁 Estrutura de Arquivos

```
agenda_app/
├── app.py                    ← EXECUTAR AQUI
├── agenda_manager.py         ← Lógica de negócio
├── config.json               ← Base de dados (JSON)
├── requirements.txt          ← Dependências
├── test_api.py              ← Testes automáticos
├── QUICK_START.md           ← Este arquivo
├── README.md                ← Documentação completa
├── INTEGRATION.md           ← Como integrar com chatbot
└── templates/
    └── index.html           ← Interface web
```

---

## 🧪 Testar Tudo

```bash
# Terminal 1 - Iniciar servidor
python app.py

# Terminal 2 - Rodar testes
python test_api.py
```

**Resultado esperado:**
```
✅ Health Check
✅ Listando Profissionais
✅ Datas Disponíveis
✅ Horários Disponíveis
✅ Criar Agendamento
✅ Listar Agendamentos
✅ Dashboard
```

---

## 🔧 Configuração

Edite `config.json` para:
- Alterar nomes/especialidades dos profissionais
- Adicionar/remover procedimentos
- Mudar horários de funcionamento
- Adicionar feriados
- Ajustar duração de procedimentos

---

## 🐛 Troubleshooting

### Porta 5001 já em uso?
```bash
# Encontrar processo usando porta 5001
netstat -ano | findstr :5001

# Ou executar em porta diferente (editar app.py linha final)
python app.py --port 5002
```

### Erro "ModuleNotFoundError: No module named 'flask'"
```bash
pip install -r requirements.txt
```

### Config.json não encontrado?
Certifique-se de executar `python app.py` do diretório `agenda_app`.

---

## 🌐 Integração com Chatbot

Ver [INTEGRATION.md](./INTEGRATION.md) para instruções de como conectar com o projeto do WhatsApp chatbot.

**Resumo:**
1. Agenda rodando em porta 5001
2. Chatbot chama `http://localhost:5001/api/...`
3. Agendamentos aparecem no dashboard

---

## 📞 Suporte

Para dúvidas, consulte:
- `README.md` - Documentação completa
- `INTEGRATION.md` - Como integrar projetos
- `app.py` - Veja comentários no código

---

**Pronto para começar?** Execute: `python app.py` 🚀

```
