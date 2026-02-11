from flask import Flask, render_template, request, jsonify, make_response
from flask_cors import CORS
from flask_compress import Compress
from agenda_manager_db import AgendaManagerDB
from whatsapp_integration import registrar_whatsapp
from cache_manager import cache_profissionais, cache_procedimentos, cache_dashboard, limpar_todo_cache
from datetime import datetime, timedelta
from database import verificar_conexao_banco
from logger_config import configurar_logging
import logging
import os
from dotenv import load_dotenv
import json

# Carregar variáveis de ambiente
load_dotenv()

# Configurar logging primeiro
configurar_logging(
    nivel=logging.DEBUG if os.getenv('FLASK_ENV') == 'development' else logging.INFO
)

logger = logging.getLogger(__name__)

# Criar app Flask
app = Flask(__name__)
CORS(app)
Compress(app)  # Ativar compressão gzip

logger.info("🚀 Iniciando aplicação...")

# Inicializar gerenciador de agenda
try:
    agenda = AgendaManagerDB()
    logger.info("✅ AgendaManagerDB inicializado com sucesso")
except Exception as e:
    logger.error(f"❌ Erro ao inicializar AgendaManagerDB: {e}", exc_info=True)
    agenda = None

# ============================================================
# HEALTH CHECK
# ============================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        db_ok = verificar_conexao_banco()
        status = 'ok' if db_ok else 'database_error'
        
        return jsonify({
            'status': status,
            'timestamp': datetime.now().isoformat(),
            'database': 'connected' if db_ok else 'disconnected'
        }), 200 if db_ok else 503
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# ============================================================
# ERROR HANDLERS
# ============================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'erro': 'Endpoint não encontrado'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal Server Error: {error}")
    return jsonify({'erro': 'Erro interno do servidor'}), 500

@app.before_request
def validate_request():
    """Validação básica de requisição"""
    if request.method == 'POST' and request.is_json is False and request.data:
        return jsonify({'erro': 'Content-Type must be application/json'}), 400

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def adicionar_cache_headers(resposta, max_age=300):
    """Adiciona headers de cache HTTP à resposta"""
    resposta.headers['Cache-Control'] = f'public, max-age={max_age}'
    resposta.headers['Expires'] = (datetime.now() + timedelta(seconds=max_age)).strftime('%a, %d %b %Y %H:%M:%S GMT')
    return resposta

# ============================================================
# ROTAS API - PROFISSIONAIS
# ============================================================

@app.route('/api/profissionais', methods=['GET'])
def get_profissionais():
    """Retorna lista de profissionais com cache"""
    try:
        # Tentar obter do cache primeiro
        dados_em_cache = cache_profissionais.obter('lista_profissionais')
        if dados_em_cache:
            resposta = make_response(jsonify(dados_em_cache))
            return adicionar_cache_headers(resposta, max_age=300), 200
        
        # Se não estiver em cache, buscar do banco
        if not agenda:
            return jsonify({'erro': 'Sistema não inicializado'}), 503
            
        profissionais = agenda.obter_profissionais_lista()
        cache_profissionais.definir('lista_profissionais', profissionais)
        
        resposta = make_response(jsonify(profissionais))
        return adicionar_cache_headers(resposta, max_age=300), 200
    except Exception as e:
        logger.error(f"Erro ao obter profissionais: {e}")
        return jsonify({'erro': 'Erro ao carregar profissionais. Tente novamente.'}), 500

@app.route('/api/profissionais/<int:prof_id>', methods=['GET'])
def get_profissional(prof_id):
    """Retorna detalhes de uma profissional"""
    try:
        if not agenda:
            return jsonify({'erro': 'Sistema não inicializado'}), 503
            
        prof = agenda.obter_profissional(prof_id)
        if not prof:
            return jsonify({'erro': 'Profissional não encontrada'}), 404
        return jsonify(prof), 200
    except Exception as e:
        logger.error(f"Erro ao obter profissional {prof_id}: {e}")
        return jsonify({'erro': 'Erro ao carregar profissional'}), 500

# ============================================================
# ROTAS API - PROCEDIMENTOS
# ============================================================

@app.route('/api/profissionais/<int:prof_id>/procedimentos', methods=['GET'])
def get_procedimentos(prof_id):
    """Retorna procedimentos de uma profissional com cache"""
    try:
        # Tentar obter do cache
        cache_key = f'procedimentos_{prof_id}'
        dados_em_cache = cache_procedimentos.obter(cache_key)
        if dados_em_cache:
            resposta = make_response(jsonify(dados_em_cache))
            return adicionar_cache_headers(resposta, max_age=300), 200
        
        # Se não estiver em cache, buscar do banco
        if not agenda:
            return jsonify({'erro': 'Sistema não inicializado'}), 503
            
        procedimentos = agenda.obter_procedimentos_profissional(prof_id)
        if not procedimentos:
            return jsonify({'erro': 'Profissional ou procedimentos não encontrados'}), 404
        
        cache_procedimentos.definir(cache_key, procedimentos)
        resposta = make_response(jsonify(procedimentos))
        return adicionar_cache_headers(resposta, max_age=300), 200
    except Exception as e:
        logger.error(f"Erro ao obter procedimentos da profissional {prof_id}: {e}")
        return jsonify({'erro': 'Erro ao carregar procedimentos'}), 500

# ============================================================
# ROTAS API - DISPONIBILIDADE
# ============================================================

@app.route('/api/profissionais/<int:prof_id>/datas-disponiveis', methods=['GET'])
def get_datas_disponiveis(prof_id):
    """Retorna datas disponíveis para agendamento"""
    try:
        if not agenda:
            return jsonify({'erro': 'Sistema não inicializado'}), 503
            
        dias_futuros = request.args.get('dias_futuros', 30, type=int)
        datas = agenda.gerar_datas_disponiveis(prof_id, dias_futuros=dias_futuros)
        return jsonify({'datas': datas}), 200
    except Exception as e:
        logger.error(f"Erro ao obter datas disponíveis para profissional {prof_id}: {e}")
        return jsonify({'erro': 'Erro ao carregar datas disponíveis'}), 500

@app.route('/api/profissionais/<int:prof_id>/horarios', methods=['GET'])
def get_horarios(prof_id):
    """Retorna horários disponíveis para uma data e procedimento"""
    try:
        if not agenda:
            return jsonify({'erro': 'Sistema não inicializado'}), 503
            
        data = request.args.get('data')  # Formato: DD/MM/YYYY
        procedimento_id = request.args.get('procedimento_id', type=int)
        
        if not data or not procedimento_id:
            return jsonify({'erro': 'Parâmetros data e procedimento_id são obrigatórios'}), 400
        
        horarios = agenda.gerar_horarios_disponiveis(prof_id, data, procedimento_id)
        return jsonify({'horarios': horarios}), 200
    except Exception as e:
        logger.error(f"Erro ao obter horários para profissional {prof_id}: {e}")
        return jsonify({'erro': 'Erro ao carregar horários'}), 500
    procedimento_id = request.args.get('procedimento_id', type=int)
    
    if not data or not procedimento_id:
        return jsonify({'erro': 'Parâmetros data e procedimento_id são obrigatórios'}), 400
    
    horarios = agenda.gerar_horarios_disponiveis(prof_id, data, procedimento_id)
    return jsonify({'horarios': horarios}), 200


# ============================================================
# ROTAS API - AGENDAMENTOS
# ============================================================

@app.route('/api/agendamentos', methods=['POST'])
def criar_agendamento():
    """Cria um novo agendamento"""
    try:
        if not agenda:
            return jsonify({'erro': 'Sistema não inicializado'}), 503
            
        dados = request.get_json()
        
        if not dados:
            return jsonify({'erro': 'Dados inválidos'}), 400
        
        # Validar dados obrigatórios - aceitar tanto prof_id quanto profissional_id
        prof_id = dados.get('prof_id') or dados.get('profissional_id')
        data = dados.get('data')
        hora = dados.get('hora')
        cliente_nome = dados.get('cliente_nome')
        cliente_telefone = dados.get('cliente_telefone')
        procedimento_id = dados.get('procedimento_id')
        procedimento_nome = dados.get('procedimento_nome')
        
        campos_obrigatorios = {
            'profissional_id': prof_id,
            'data': data,
            'hora': hora,
            'cliente_nome': cliente_nome,
            'cliente_telefone': cliente_telefone,
            'procedimento_id': procedimento_id,
            'procedimento_nome': procedimento_nome
        }
        
        campos_faltando = [k for k, v in campos_obrigatorios.items() if not v]
        
        if campos_faltando:
            return jsonify({'erro': f'Campos obrigatórios: {", ".join(campos_faltando)}'}), 400
        
        sucesso, mensagem, agendamento_id = agenda.criar_agendamento(
            prof_id=prof_id,
            data_str=data,
            horario=hora,
            cliente_nome=cliente_nome.strip(),
            cliente_telefone=cliente_telefone.strip(),
            procedimento_id=procedimento_id,
            procedimento_nome=procedimento_nome
        )
        
        if not sucesso:
            logger.warning(f"Falha ao criar agendamento: {mensagem}")
            return jsonify({'erro': mensagem}), 400
        
        # Limpar cache após criar agendamento
        limpar_todo_cache()
        
        logger.info(f"Agendamento criado: {agendamento_id}")
        return jsonify({
            'sucesso': True,
            'mensagem': mensagem,
            'agendamento_id': agendamento_id
        }), 201
    except Exception as e:
        logger.error(f"Erro ao criar agendamento: {str(e)}")
        return jsonify({'erro': 'Erro ao processar agendamento. Tente novamente.'}), 500

@app.route('/api/profissionais/<int:prof_id>/agendamentos', methods=['GET'])
def get_agendamentos(prof_id):
    """Retorna agendamentos de uma profissional"""
    try:
        if not agenda:
            return jsonify({'erro': 'Sistema não inicializado'}), 503
            
        result = agenda.obter_agendamentos_profissional(prof_id)
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Erro ao obter agendamentos da profissional {prof_id}: {e}")
        return jsonify({'erro': 'Erro ao carregar agendamentos'}), 500

@app.route('/api/agendamentos/<agendamento_id>', methods=['GET'])
def get_agendamento(agendamento_id):
    """Retorna detalhes de um agendamento"""
    return jsonify({'erro': 'Endpoint não implementado'}), 501

@app.route('/api/agendamentos/<agendamento_id>', methods=['DELETE'])
def deletar_agendamento(agendamento_id):
    """Cancela um agendamento"""
    try:
        if not agenda:
            return jsonify({'erro': 'Sistema não inicializado'}), 503
            
        try:
            agendamento_id_int = int(agendamento_id)
        except ValueError:
            return jsonify({'erro': 'ID de agendamento inválido'}), 400
        
        sucesso, mensagem = agenda.cancelar_agendamento(agendamento_id_int)
        
        if not sucesso:
            return jsonify({'erro': mensagem}), 404
        
        # Limpar cache após cancelar agendamento
        limpar_todo_cache()
        
        return jsonify({'sucesso': True, 'mensagem': mensagem}), 200
    except Exception as e:
        logger.error(f"Erro ao cancelar agendamento {agendamento_id}: {e}")
        return jsonify({'erro': 'Erro ao cancelar agendamento'}), 500

# ============================================================
# ROTAS API - DASHBOARD
# ============================================================

@app.route('/api/dashboard', methods=['GET'])
def get_dashboard():
    """Retorna informações para o dashboard com cache"""
    try:
        if not agenda:
            return jsonify({'erro': 'Sistema não inicializado'}), 503
            
        # Tentar obter do cache (mais curto porque é mais dinâmico)
        dados_em_cache = cache_dashboard.obter('dashboard')
        if dados_em_cache:
            resposta = make_response(jsonify(dados_em_cache))
            return adicionar_cache_headers(resposta, max_age=60), 200
        
        # Se não estiver em cache, buscar do banco
        from database import SessionLocal, Agendamento
        db = SessionLocal()
        try:
            profissionais_list = agenda.obter_profissionais_lista()
            
            profissionais_data = []
            total_geral = 0
            
            for prof in profissionais_list:
                agendamentos = db.query(Agendamento).filter(
                    Agendamento.profissional_id == prof['id']
                ).all()
                
                confirmados = len([a for a in agendamentos if a.status == 'confirmado'])
                cancelados = len([a for a in agendamentos if a.status == 'cancelado'])
                
                profissionais_data.append({
                    'id': prof['id'],
                    'nome': prof['nome'],
                    'especialidade': prof['especialidade'],
                    'total_agendamentos': len(agendamentos),
                    'confirmados': confirmados,
                    'cancelados': cancelados
                })
                total_geral += len(agendamentos)
            
            dashboard_data = {
                'clinica': {
                    'nome': agenda.config['clinica']['nome'],
                    'horario_funcionamento': agenda.config['clinica']['horario_funcionamento']
                },
                'profissionais': profissionais_data,
                'total_agendamentos': total_geral
            }
            
            cache_dashboard.definir('dashboard', dashboard_data)
            resposta = make_response(jsonify(dashboard_data))
            return adicionar_cache_headers(resposta, max_age=60), 200
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Erro ao obter dashboard: {e}")
        return jsonify({'erro': 'Erro ao carregar dashboard'}), 500

@app.route('/api/profissionais/<int:prof_id>/mes', methods=['GET'])
def get_mes(prof_id):
    """Retorna disponibilidade de um mês"""
    mes = request.args.get('mes', type=int, default=datetime.now().month)
    ano = request.args.get('ano', type=int, default=datetime.now().year)
    
    disponibilidade = agenda.obter_disponibilidade_mes(prof_id, mes, ano)
    return jsonify(disponibilidade), 200

# ============================================================
# ROTAS FRONTEND
# ============================================================

@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')

@app.route('/agenda/<int:prof_id>')
def agenda_page(prof_id):
    """Página de agenda de uma profissional"""
    prof = agenda.obter_profissional(prof_id)
    if not prof:
        return "Profissional não encontrada", 404
    return render_template('agenda.html', profissional=prof)

# ============================================================
# HEALTH CHECK
# ============================================================

@app.route('/api/health', methods=['GET'])
def health():
    """Health check da API"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'versao': '1.0.0',
        'cache': 'ativado'
    }), 200

@app.route('/api/cache/limpar', methods=['POST'])
def limpar_cache_endpoint():
    """Limpa o cache da API (admin)"""
    limpar_todo_cache()
    return jsonify({
        'sucesso': True,
        'mensagem': 'Cache limpado com sucesso'
    }), 200

# ============================================================
# ERROR HANDLERS
# ============================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'erro': 'Recurso não encontrado'}), 404

@app.errorhandler(500)
def server_error(error):
    logger.error(f"Erro interno do servidor: {error}")
    return jsonify({'erro': 'Erro interno do servidor'}), 500

if __name__ == '__main__':
    print("🚀 Iniciando API de Agenda - Marcia Rocha Beauty")
    print("=" * 70)
    print("✅ Endpoints disponíveis:")
    print("   - GET  /api/profissionais")
    print("   - GET  /api/profissionais/<id>")
    print("   - GET  /api/profissionais/<id>/procedimentos")
    print("   - GET  /api/profissionais/<id>/datas-disponiveis")
    print("   - GET  /api/profissionais/<id>/horarios?data=DD/MM/YYYY&procedimento_id=X")
    print("   - POST /api/agendamentos")
    print("   - GET  /api/profissionais/<id>/agendamentos")
    print("   - GET  /api/agendamentos/<id>")
    print("   - DEL  /api/agendamentos/<id>")
    print("   - GET  /api/dashboard")
    print("   - GET  /api/profissionais/<id>/mes?mes=2&ano=2026")
    print("\n📱 Integração WhatsApp:")
    print("   - POST /api/whatsapp/webhook (webhook do WhatsApp)")
    print("   - POST /api/whatsapp/testar (teste do chatbot)")
    print("=" * 70)
    
    # Registrar integração WhatsApp
    registrar_whatsapp(app)
    
    app.run(debug=True, host='0.0.0.0', port=5001)
