"""
Integração do Chatbot com WhatsApp via WhAPI Cloud
Centralizado na Agenda App
"""

import os
import json
import logging
from flask import Blueprint, request, jsonify
from chatbot_client import ChatbotAPIClient
import re
from typing import Optional, Dict, Tuple
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Criar blueprint para rotas de WhatsApp
whatsapp_bp = Blueprint('whatsapp', __name__, url_prefix='/api/whatsapp')

# Cliente da API
api_client = ChatbotAPIClient()

# Armazenar estado de conversas do chatbot
conversas = {}
estado_usuarios = {}

class ChatbotIntegrador:
    """Integra chatbot com a API da Agenda App"""
    
    def __init__(self):
        self.api_client = ChatbotAPIClient()
        self.estado_usuario = {}
        
    def inicializar_usuario(self, telefone_usuario: str):
        """Inicializa estado do usuário"""
        if telefone_usuario not in self.estado_usuario:
            self.estado_usuario[telefone_usuario] = {
                'etapa': 'escolha_profissional',
                'dados': {},
                'profissional_id': None,
                'procedimento_id': None
            }
    
    def processar_mensagem(self, telefone_usuario: str, mensagem: str) -> Tuple[str, Optional[bytes]]:
        """
        Processa mensagem do usuário e retorna resposta
        
        Returns:
            (resposta_texto, arquivo_para_enviar)
        """
        self.inicializar_usuario(telefone_usuario)
        usuario = self.estado_usuario[telefone_usuario]
        
        mensagem_lower = mensagem.lower().strip()
        
        # Verificar gatilhos de atendimento humano
        gatilhos_atendimento = [
            'humano', 'atendente', 'pessoa', 'falar com alguém',
            'gerente', 'supervisor', 'admin', 'responsável'
        ]
        
        if any(gatilho in mensagem_lower for gatilho in gatilhos_atendimento):
            resposta = "👋 Um atendente entrará em contato com você em breve!\n\n"
            resposta += "📞 Ou ligue para: +55 (seu telefone aqui)"
            return resposta, None
        
        # Roteamento por etapa
        if usuario['etapa'] == 'escolha_profissional':
            return self._processar_escolha_profissional(telefone_usuario, mensagem)
        elif usuario['etapa'] == 'menu_inicial':
            return self._processar_menu_inicial(telefone_usuario, mensagem)
        elif usuario['etapa'] == 'escolha_procedimento':
            return self._processar_escolha_procedimento(telefone_usuario, mensagem)
        elif usuario['etapa'] == 'agendar_dados':
            return self._processar_dados_agendamento(telefone_usuario, mensagem)
        elif usuario['etapa'] == 'agendar_escolha_data':
            return self._processar_escolha_data(telefone_usuario, mensagem)
        elif usuario['etapa'] == 'agendar_horario':
            return self._processar_escolha_horario(telefone_usuario, mensagem)
        else:
            return "Desculpe, não consegui entender. Digite 1 para voltar ao menu inicial.", None
    
    def _extrair_numero(self, texto: str) -> Optional[int]:
        """Extrai número do texto"""
        limpo = re.sub(r'[^\d]', '', texto.strip())
        if limpo:
            try:
                return int(limpo)
            except ValueError:
                return None
        return None
    
    def _processar_escolha_profissional(self, telefone: str, mensagem: str) -> Tuple[str, Optional[bytes]]:
        """Processa escolha de profissional"""
        numero = self._extrair_numero(mensagem)
        
        # Obter lista de profissionais
        sucesso, profs, msg = self.api_client.obter_profissionais()
        
        if not sucesso or not profs:
            resposta = f"Desculpe, erro ao carregar as profissionais.\n\nTente novamente em instantes."
            return resposta, None
        
        # Validar escolha
        if numero is None or numero < 1 or numero > len(profs):
            resposta = "🧘‍♀️ *Bem-vindo á Marcia Rocha Beauty!*\n\n"
            resposta += "Escolha uma profissional:\n\n"
            for i, prof in enumerate(profs, 1):
                resposta += f"{i}️⃣ {prof['nome']} - {prof['especialidade']}\n"
            return resposta, None
        
        # Armazenar profissional selecionada
        prof_selecionada = profs[numero - 1]
        usuario = self.estado_usuario[telefone]
        usuario['profissional_id'] = prof_selecionada['id']
        usuario['dados']['profissional_nome'] = prof_selecionada['nome']
        usuario['etapa'] = 'menu_inicial'
        
        resposta = f"✨ Você escolheu: *{prof_selecionada['nome']}*\n\n"
        resposta += "O que deseja fazer?\n\n"
        resposta += "1️⃣ Conhecer procedimentos\n"
        resposta += "2️⃣ Agendar um procedimento\n"
        resposta += "3️⃣ Ver valores\n"
        resposta += "4️⃣ Falar com um atendente\n"
        
        return resposta, None
    
    def _processar_menu_inicial(self, telefone: str, mensagem: str) -> Tuple[str, Optional[bytes]]:
        """Processa menu inicial"""
        numero = self._extrair_numero(mensagem)
        usuario = self.estado_usuario[telefone]
        prof_id = usuario['profissional_id']
        
        if numero == 1:
            # Conhecer procedimentos
            sucesso, procs, msg = self.api_client.obter_procedimentos(prof_id)
            
            if not sucesso:
                return f"Erro ao carregar procedimentos: {msg}", None
            
            usuario['etapa'] = 'escolha_procedimento'
            usuario['dados']['procedimentos'] = procs
            
            resposta = "📋 *Procedimentos Disponíveis*\n\n"
            for proc_id, proc_nome in procs.items():
                resposta += f"• {proc_nome}\n"
            
            resposta += "\nDigite o número do procedimento para saber mais detalhes"
            return resposta, None
        
        elif numero == 2:
            # Agendar
            usuario['etapa'] = 'agendar_dados'
            resposta = "📅 Vamos agendar seu atendimento!\n\n"
            resposta += "Qual é seu nome completo?"
            return resposta, None
        
        elif numero == 3:
            # Valores
            resposta = "💰 *Tabela de Valores*\n\n"
            resposta += "Para visualizar a tabela completa com todas as opções,\n"
            resposta += "enviaremos um arquivo PDF em breve.\n\n"
            resposta += "Deseja agendar agora?\n"
            resposta += "1️⃣ Sim, quero agendar\n"
            resposta += "2️⃣ Não, só queria consultar"
            usuario['etapa'] = 'menu_inicial'
            return resposta, None
        
        elif numero == 4:
            # Atendente
            resposta = "👋 Um atendente entrará em contato com você em breve!\n"
            usuario['etapa'] = 'menu_inicial'
            return resposta, None
        
        else:
            resposta = "Opção inválida. Digite 1, 2, 3 ou 4."
            return resposta, None
    
    def _processar_escolha_procedimento(self, telefone: str, mensagem: str) -> Tuple[str, Optional[bytes]]:
        """Processa escolha de procedimento"""
        usuario = self.estado_usuario[telefone]
        procs = usuario['dados'].get('procedimentos', {})
        
        # Encontrar procedimento
        proc_id = None
        proc_nome = None
        
        for pid, pnome in procs.items():
            if self._extrair_numero(mensagem) == int(pid):
                proc_id = pid
                proc_nome = pnome
                break
        
        if not proc_id:
            resposta = "Procedimento não encontrado.\n\n"
            resposta += "Digite o número do procedimento para mais informações."
            return resposta, None
        
        usuario['procedimento_id'] = int(proc_id)
        usuario['dados']['procedimento_nome'] = proc_nome
        usuario['etapa'] = 'agendar_dados'
        
        resposta = f"✨ *{proc_nome}*\n\n"
        resposta += "Ótima escolha! Vamos agendar?\n\n"
        resposta += "Qual é seu nome completo?"
        
        return resposta, None
    
    def _processar_dados_agendamento(self, telefone: str, mensagem: str) -> Tuple[str, Optional[bytes]]:
        """Processa coleta de dados para agendamento"""
        usuario = self.estado_usuario[telefone]
        
        if 'nome_cliente' not in usuario['dados']:
            nome = mensagem.strip()
            if len(nome) < 3:
                return "Por favor, forneça um nome válido com pelo menos 3 caracteres.", None
            
            usuario['dados']['nome_cliente'] = nome
            resposta = f"✨ Olá {nome}!\n\n"
            resposta += "Qual é seu telefone para contato?\n"
            resposta += "(Digite incluindo código de área, ex: (11) 98765-4321)"
            return resposta, None
        
        elif 'telefone_cliente' not in usuario['dados']:
            telefone_cliente = mensagem.strip()
            limpo = re.sub(r'[^\d]', '', telefone_cliente)
            
            if len(limpo) < 10:
                return "Telefone inválido. Por favor, forneça um número válido.", None
            
            usuario['dados']['telefone_cliente'] = limpo
            usuario['etapa'] = 'agendar_escolha_data'
            
            # Obter datas disponíveis
            prof_id = usuario['profissional_id']
            sucesso, datas, msg = self.api_client.obter_datas_disponiveis(prof_id, dias_futuros=7)
            
            if not sucesso:
                return f"Erro ao carregar datas: {msg}", None
            
            usuario['dados']['datas_disponiveis'] = datas
            
            resposta = "📅 *Datas Disponíveis*\n\n"
            for i, data in enumerate(datas, 1):
                data_obj = datetime.strptime(data, "%d/%m/%Y")
                dia_semana = self._get_dia_semana(data_obj.weekday())
                resposta += f"{i}️⃣ {data} ({dia_semana})\n"
            
            resposta += "\nEscolha uma data digitando o número"
            return resposta, None
        
        return "Erro no fluxo. Digite 1 para voltar ao menu.", None
    
    def _processar_escolha_data(self, telefone: str, mensagem: str) -> Tuple[str, Optional[bytes]]:
        """Processa escolha de data"""
        numero = self._extrair_numero(mensagem)
        usuario = self.estado_usuario[telefone]
        datas = usuario['dados'].get('datas_disponiveis', [])
        
        if numero is None or numero < 1 or numero > len(datas):
            resposta = "Data inválida. Digite o número da data desejada."
            return resposta, None
        
        data_selecionada = datas[numero - 1]
        usuario['dados']['data'] = data_selecionada
        usuario['etapa'] = 'agendar_horario'
        
        # Obter horários
        prof_id = usuario['profissional_id']
        proc_id = usuario['procedimento_id']
        
        sucesso, horarios, msg = self.api_client.obter_horarios(prof_id, data_selecionada, proc_id)
        
        if not sucesso:
            return f"Erro ao carregar horários: {msg}", None
        
        usuario['dados']['horarios_disponiveis'] = horarios
        
        resposta = f"⏰ *Horários Disponíveis para {data_selecionada}*\n\n"
        for i, horario in enumerate(horarios, 1):
            resposta += f"{i}️⃣ {horario}\n"
        
        resposta += "\nEscolha um horário digitando o número"
        return resposta, None
    
    def _processar_escolha_horario(self, telefone: str, mensagem: str) -> Tuple[str, Optional[bytes]]:
        """Processa escolha de horário e cria agendamento"""
        numero = self._extrair_numero(mensagem)
        usuario = self.estado_usuario[telefone]
        horarios = usuario['dados'].get('horarios_disponiveis', [])
        
        if numero is None or numero < 1 or numero > len(horarios):
            resposta = "Horário inválido. Digite o número do horário desejado."
            return resposta, None
        
        horario_selecionado = horarios[numero - 1]
        
        # Armazenar dados antes de limpar
        dados = usuario['dados'].copy()
        
        # Criar agendamento
        sucesso, agendamento_id, msg = self.api_client.criar_agendamento(
            prof_id=usuario['profissional_id'],
            data=dados['data'],
            hora=horario_selecionado,
            cliente_nome=dados['nome_cliente'],
            cliente_telefone=dados['telefone_cliente'],
            procedimento_id=usuario['procedimento_id'],
            procedimento_nome=dados['procedimento_nome']
        )
        
        if not sucesso:
            return f"Erro ao agendar: {msg}\n\nTente outro horário.", None
        
        # Sucesso!
        usuario['etapa'] = 'menu_inicial'
        usuario['procedimento_id'] = None
        usuario['dados'] = {}
        
        resposta = "✅ *AGENDAMENTO CONFIRMADO!*\n\n"
        resposta += f"👤 Paciente: {dados['nome_cliente']}\n"
        resposta += f"🧘‍♀️ Profissional: {dados['profissional_nome']}\n"
        resposta += f"💅 Procedimento: {dados['procedimento_nome']}\n"
        resposta += f"📅 Data: {dados['data']}\n"
        resposta += f"⏰ Horário: {horario_selecionado}\n\n"
        resposta += f"ID do Agendamento: {agendamento_id}\n\n"
        resposta += "Obrigada por escolher nossa clínica! 💕\n\n"
        resposta += "Posso ajudar em mais algo?\n"
        resposta += "1️⃣ Sim\n"
        resposta += "2️⃣ Não, obrigada"
        
        return resposta, None
    
    def _get_dia_semana(self, num: int) -> str:
        """Retorna nome do dia da semana"""
        dias = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sab', 'Dom']
        return dias[num]


# Instância global do integrador
integrador = ChatbotIntegrador()


# ============================================================
# ROTAS FLASK PARA WHATSAPP
# ============================================================

@whatsapp_bp.route('/webhook', methods=['GET'])
def webhook_verify():
    """Verifica webhook do WhatsApp"""
    verify_token = os.getenv('WHATSAPP_VERIFY_TOKEN', 'agroclimate')
    
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    
    if token == verify_token:
        return challenge, 200
    
    return 'Token inválido', 403


@whatsapp_bp.route('/webhook', methods=['POST'])
def webhook_message():
    """Recebe mensagens do WhatsApp"""
    try:
        dados = request.get_json()
        
        # Verificar se é mensagem de entrada
        if dados.get('entry'):
            for entry in dados['entry']:
                for messaging_event in entry.get('messaging', []):
                    if messaging_event.get('message'):
                        telefone_usuario = messaging_event['sender']['id']
                        texto_mensagem = messaging_event['message'].get('text', '').get('body', '')
                        
                        if texto_mensagem:
                            logger.info(f"Mensagem recebida de {telefone_usuario}: {texto_mensagem}")
                            
                            # Processar mensagem
                            resposta, arquivo = integrador.processar_mensagem(telefone_usuario, texto_mensagem)
                            
                            # Enviar resposta (aqui você integra com seu cliente WhatsApp)
                            logger.info(f"Respondendo para {telefone_usuario}: {resposta}")
        
        return jsonify({'status': 'ok'}), 200
    
    except Exception as e:
        logger.error(f"Erro ao processar webhook: {str(e)}")
        return jsonify({'erro': str(e)}), 500


@whatsapp_bp.route('/testar', methods=['POST'])
def testar_chatbot():
    """Endpoint para testar o chatbot (sem WhatsApp)"""
    dados = request.get_json()
    telefone = dados.get('telefone', 'usuario_teste_123')
    mensagem = dados.get('mensagem', '')
    
    resposta, _ = integrador.processar_mensagem(telefone, mensagem)
    
    return jsonify({
        'telefone': telefone,
        'mensagem': mensagem,
        'resposta': resposta
    }), 200


# ============================================================
# FUNÇÃO PARA ADICIONAR O BLUEPRINT
# ============================================================

def registrar_whatsapp(app):
    """Registra blueprint de WhatsApp na aplicação Flask"""
    app.register_blueprint(whatsapp_bp)
    logger.info("✅ Integração WhatsApp registrada")


if __name__ == "__main__":
    # Teste local
    bot = ChatbotIntegrador()
    
    print("🤖 TESTE DO CHATBOT INTEGRADO")
    print("=" * 70)
    
    telefone_teste = "5511987654321"
    
    mensagens = [
        "Oi",
        "1",  # Escolher Rayssa
        "2",  # Agendar
        "Maria Silva",  # Nome
        "(11) 98765-4321",  # Telefone
        "1",  # Data
        "1",  # Horário
    ]
    
    for msg in mensagens:
        print(f"\n👤 Usuário: {msg}")
        resposta, _ = bot.processar_mensagem(telefone_teste, msg)
        print(f"🤖 Bot: {resposta[:150]}...")
    
    print("\n" + "=" * 70)
    print("✅ Teste concluído!")
