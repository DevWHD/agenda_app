# 📅 Projeto Agenda - Marcia Rocha Beauty

**PROJETO INDEPENDENTE / STANDALONE**

Sistema de gerenciamento de agenda profissional com frontend para visualização e gerencimento de agendamentos.

## 📁 Estrutura do Projeto

```
agenda_app/
├── app.py                    # Backend Flask (API + servidor web)
├── agenda_manager.py         # Gerenciador de agenda
├── config.json              # Configuração de profissionais e horários
├── requirements.txt         # Dependências Python
├── templates/
│   └── index.html           # Frontend (Dashboard + Agenda)
└── README.md               # Este arquivo
```

## 🚀 Como Executar

### 1. Instalar Dependências

```bash
cd c:\Users\Whendel\Documents\agenda_app
pip install -r requirements.txt
```

### 2. Iniciar o Servidor

```bash
python app.py
```

O servidor iniciará em: **http://localhost:5001**

## 🎯 Funcionalidades

### Frontend (Interface Web)
- ✅ **Dashboard** com cards de profissionais
- ✅ **Visualização de agendamentos** por profissional
- ✅ **Estatísticas** (total, confirmados, cancelados)
- ✅ **Cancelamento de agendamentos**
- ✅ **Design responsivo** (mobile-friendly)
- ✅ **Interface intuitiva** com emojis e cores

### Backend API
- ✅ **CRUD completo** de agendamentos
- ✅ **Gerenciamento de disponibilidade**
- ✅ **Suporte CORS** para chamadas externas
- ✅ **Endpoints RESTful**
- ✅ **Validação de conflitos** de horários

## 📡 Endpoints da API

### Profissionais
```
GET /api/profissionais                    # Lista todas as profissionais
GET /api/profissionais/<id>               # Detalhes de uma profissional
GET /api/profissionais/<id>/procedimentos # Procedimentos de uma profissional
```

### Disponibilidade
```
GET /api/profissionais/<id>/datas-disponiveis              # Próximas datas
GET /api/profissionais/<id>/horarios?data=DD/MM/YYYY&proc=X # Horários
```

### Agendamentos
```
POST /api/agendamentos                    # Criar agendamento
GET /api/profissionais/<id>/agendamentos  # Listar agendamentos
GET /api/agendamentos/<id>                # Detalhes de agendamento
DELETE /api/agendamentos/<id>             # Cancelar agendamento
```

### Dashboard
```
GET /api/dashboard                        # Dados para dashboard
GET /api/profissionais/<id>/mes           # Disponibilidade do mês
GET /api/health                           # Health check
```

## 📊 Exemplo de Requisição

### Criar Agendamento
```json
POST /api/agendamentos
{
  "prof_id": 1,
  "data": "11/02/2026",
  "hora": "10:00",
  "cliente_nome": "Maria Silva",
  "cliente_telefone": "11987654321",
  "procedimento_id": 101,
  "procedimento_nome": "Pedicure"
}
```

### Resposta
```json
{
  "sucesso": true,
  "mensagem": "Agendamento confirmado",
  "agendamento_id": "AG11234567890"
}
```

## 👩‍⚕️ Profissionais Configuradas

| ID | Nome | Especialidade | Dias | Procedimentos |
|---|---|---|---|---|
| 1 | Rayssa Tomaz | Unhas e Pés | Seg-Sab | 5 |
| 2 | Marcia Rocha | Beleza Avançada | Seg-Sex | 10 |
| 3 | Mirian Rocha | Cuidados com Pele | Seg-Sab | 2 |

## ⚙️ Configuração

Editar `config.json` para:
- Alterar horários de funcionamento
- Adicionar/remover profissionais
- Mudar duração de procedimentos
- Adicionar feriados
- Configurar intervalo entre clientes

## 🔧 Integração com Chatbot

O chatbot (`pra esposa/`) se conecta via API a este projeto:

```python
# Exemplo de chamada do chatbot
requests.get('http://localhost:5001/api/profissionais/1/horarios?data=11/02/2026&procedimento_id=101')
```

## 📝 Notas Importantes

- ✅ Dados persistem em `config.json`
- ✅ API roda na porta **5001**
- ✅ Chatbot roda na porta **5000**
- ✅ Suporta requisições Cross-Origin (CORS)
- ✅ Validação automática de conflitos

## 🌐 Hospedagem

Para hospedar este projeto:

1. **Servidor Local**: `python app.py`
2. **Em Nuvem**: Heroku, Vercel, AWS, DigitalOcean, etc.
3. **Docker**: Criar Dockerfile com Python + Flask

## 📞 Suporte

Projeto desenvolvido para **Marcia Rocha Beauty** 💫

---

**Versão**: 1.0.0  
**Última atualização**: Fevereiro 2026
