"""
Gerenciador de Agenda - Versão PostgreSQL
Usa SQLAlchemy ORM para PostgreSQL
"""
from datetime import datetime, timedelta, date, time
from typing import List, Dict, Tuple, Optional
from database import SessionLocal, Profissional, Procedimento, Agendamento, Feriado, HorarioFuncionamento, executar_com_retry
import logging
import time

logger = logging.getLogger(__name__)


def com_retry(funcao):
    """Decorator para executar funcoes com retry automático"""
    def wrapper(*args, **kwargs):
        max_tentativas = 3
        for tentativa in range(max_tentativas):
            try:
                return funcao(*args, **kwargs)
            except Exception as e:
                if tentativa < max_tentativas - 1:
                    tempo_espera = 2 ** tentativa
                    logger.warning(f"Erro em {funcao.__name__} (tentativa {tentativa + 1}): {e}. Tentando novamente em {tempo_espera}s...")
                    time.sleep(tempo_espera)
                else:
                    logger.error(f"Falha após {max_tentativas} tentativas em {funcao.__name__}: {e}")
                    raise
    return wrapper


class AgendaManagerDB:
    """Gerenciador de agenda usando PostgreSQL"""

    def __init__(self):
        # Configuração da clínica
        self.config = {
            'clinica': {
                'nome': 'Marcia Rocha Beauty',
                'horario_funcionamento': {
                    'segunda': '09:00 - 18:00',
                    'terca': '09:00 - 18:00',
                    'quarta': '09:00 - 18:00',
                    'quinta': '09:00 - 18:00',
                    'sexta': '09:00 - 18:00',
                    'sabado': '09:00 - 18:00',
                    'domingo': 'Fechado'
                }
            }
        }

    @com_retry
    def obter_profissional(self, prof_id: int) -> Optional[Dict]:
        """Obtém detalhes de uma profissional"""
        db = SessionLocal()
        try:
            prof = db.query(Profissional).filter(Profissional.id == prof_id).first()
            return prof.to_dict() if prof else None
        except Exception as e:
            logger.error(f"Erro ao obter profissional {prof_id}: {e}")
            raise
        finally:
            db.close()

    @com_retry
    def obter_profissionais_lista(self) -> List[Dict]:
        """Retorna lista de profissionais"""
        db = SessionLocal()
        try:
            profs = db.query(Profissional).filter(Profissional.ativo == True).all()
            return [p.to_dict() for p in profs]
        except Exception as e:
            logger.error(f"Erro ao obter lista de profissionais: {e}")
            raise
        finally:
            db.close()

    @com_retry
    def obter_procedimentos_profissional(self, prof_id: int) -> Dict:
        """Obtém procedimentos de uma profissional como dicionário"""
        db = SessionLocal()
        try:
            procs = db.query(Procedimento).filter(
                Procedimento.profissional_id == prof_id,
                Procedimento.ativo == True
            ).all()
            
            resultado = {}
            for proc in procs:
                resultado[proc.codigo] = {
                    'nome': proc.nome,
                    'descricao': proc.descricao,
                    'duracao_minutos': proc.duracao_minutos,
                    'preco': proc.preco
                }
            return resultado
        except Exception as e:
            logger.error(f"Erro ao obter procedimentos da profissional {prof_id}: {e}")
            raise
        finally:
            db.close()

    def eh_feriado(self, data_str: str) -> bool:
        """Verifica se a data é um feriado (formato DD/MM)"""
        try:
            dia, mes = data_str.split('/')
            db = SessionLocal()
            try:
                feriado = db.query(Feriado).filter(
                    Feriado.data == date(2026, int(mes), int(dia))
                ).first()
                return feriado is not None
            except Exception as e:
                logger.error(f"Erro ao verificar feriado para {data_str}: {e}")
                return False
            finally:
                db.close()
        except ValueError as e:
            logger.warning(f"Data com formato inválido: {data_str}")
            return False
        except Exception as e:
            logger.error(f"Erro inesperado ao verificar feriado: {e}")
            return False

    @com_retry
    def gerar_datas_disponiveis(self, prof_id: int, dias_futuros: int = 30) -> List[str]:
        """Gera lista de datas disponíveis para agendamento"""
        db = SessionLocal()
        try:
            prof = db.query(Profissional).filter(Profissional.id == prof_id).first()
            if not prof:
                logger.warning(f"Profissional {prof_id} não encontrada")
                return []

            datas = []
            hoje = date.today()

            for i in range(dias_futuros):
                data = hoje + timedelta(days=i)
                data_str = data.strftime('%d/%m/%Y')

                # Verificar se não é feriado
                if self.eh_feriado(data_str):
                    continue

                # Verificar se é dia útil
                dia_semana = ['segunda', 'terca', 'quarta', 'quinta', 'sexta', 'sabado', 'domingo'][data.weekday()]
                
                if prof.dias_uteis and dia_semana not in prof.dias_uteis:
                    continue

                datas.append(data_str)

            return sorted(datas[:30])
        except Exception as e:
            logger.error(f"Erro ao gerar datas disponíveis para profissional {prof_id}: {e}")
            raise
        finally:
            db.close()

    @com_retry
    def gerar_horarios_disponiveis(self, prof_id: int, data_str: str, proc_id: int) -> List[str]:
        """Gera horários disponíveis para um dia e procedimento específicos"""
        db = SessionLocal()
        try:
            prof = db.query(Profissional).filter(Profissional.id == prof_id).first()
            if not prof:
                logger.warning(f"Profissional {prof_id} não encontrada")
                return []

            try:
                dia, mes, ano = data_str.split('/')
                data = date(int(ano), int(mes), int(dia))
            except ValueError as e:
                logger.warning(f"Data com formato inválido: {data_str}")
                return []

            # Obter horário de funcionamento do dia
            dia_semana = ['segunda', 'terca', 'quarta', 'quinta', 'sexta', 'sabado', 'domingo'][data.weekday()]
            horario_func = db.query(HorarioFuncionamento).filter(
                HorarioFuncionamento.dia_semana == dia_semana
            ).first()

            if not horario_func or not horario_func.hora_abertura or not horario_func.hora_fechamento:
                logger.warning(f"Horário de funcionamento não encontrado para {dia_semana}")
                return []

            # Obter agendamentos do dia
            agendamentos_dia = db.query(Agendamento).filter(
                Agendamento.profissional_id == prof_id,
                Agendamento.data_agendamento == data,
                Agendamento.status == 'confirmado'
            ).all()

            horas_ocupadas = set()
            for agend in agendamentos_dia:
                if agend.hora_inicio:
                    horas_ocupadas.add(agend.hora_inicio.strftime('%H:%M'))

            # Gerar horários disponíveis
            hora_atual = datetime.combine(data, horario_func.hora_abertura)
            hora_fim = datetime.combine(data, horario_func.hora_fechamento)

            horarios = []
            while hora_atual < hora_fim:
                hora_str = hora_atual.strftime('%H:%M')
                if hora_str not in horas_ocupadas:
                    horarios.append(hora_str)
                hora_atual += timedelta(minutes=30)

            return horarios
        except Exception as e:
            logger.error(f"Erro ao gerar horários para profissional {prof_id} em {data_str}: {e}")
            raise
        finally:
            db.close()

    @com_retry
    def obter_agendamentos_profissional(self, prof_id: int) -> Dict:
        """Obtém agendamentos de uma profissional"""
        db = SessionLocal()
        try:
            agendamentos = db.query(Agendamento).filter(
                Agendamento.profissional_id == prof_id
            ).all()

            return {
                'agendamentos': [
                    {
                        'id': a.id,
                        'codigo_agendamento': a.codigo_agendamento,
                        'cliente_nome': a.cliente_nome,
                        'cliente_telefone': a.cliente_telefone,
                        'procedimento_nome': a.procedimento.nome if a.procedimento else 'N/A',
                        'procedimento_id': a.procedimento_id,
                        'data': a.data_agendamento.strftime('%d/%m/%Y'),
                        'hora': a.hora_inicio.strftime('%H:%M') if a.hora_inicio else None,
                        'status': a.status
                    }
                    for a in agendamentos
                ]
            }
        except Exception as e:
            logger.error(f"Erro ao obter agendamentos da profissional {prof_id}: {e}")
            raise
        finally:
            db.close()

    @com_retry
    def criar_agendamento(self, prof_id: int, data_str: str, horario: str, 
                         cliente_nome: str, cliente_telefone: str, 
                         procedimento_id: int, procedimento_nome: str) -> Tuple[bool, str, Optional[str]]:
        """Cria novo agendamento"""
        
        # Validações
        if not self.validar_data(data_str):
            return False, "Data inválida ou fora do período permitido", None
        
        if not self.validar_telefone(cliente_telefone):
            return False, "Telefone deve ter 10-11 dígitos", None
        
        if not self.validar_cliente(cliente_nome):
            return False, "Nome deve ter entre 3-100 caracteres", None

        db = SessionLocal()
        try:
            dia, mes, ano = data_str.split('/')
            data = date(int(ano), int(mes), int(dia))
            hora_parts = horario.split(':')
            hora = time(int(hora_parts[0]), int(hora_parts[1]))

            # Gerar código
            timestamp = datetime.now().strftime('%d%m%y%H%M%S')
            codigo = f'AG{timestamp}'

            # Criar agendamento
            agendamento = Agendamento(
                codigo_agendamento=codigo,
                profissional_id=prof_id,
                procedimento_id=procedimento_id,
                cliente_nome=cliente_nome,
                cliente_telefone=cliente_telefone,
                data_agendamento=data,
                hora_inicio=hora,
                status='confirmado'
            )

            db.add(agendamento)
            db.commit()
            
            logger.info(f"Agendamento criado: {codigo}")
            return True, "Agendamento criado com sucesso", codigo
        except Exception as e:
            db.rollback()
            logger.error(f"Erro ao criar agendamento: {e}")
            return False, f"Erro ao criar agendamento: {str(e)}", None
        finally:
            db.close()

    @com_retry
    def cancelar_agendamento(self, agendamento_id: int) -> Tuple[bool, str]:
        """Cancela um agendamento"""
        db = SessionLocal()
        try:
            agend = db.query(Agendamento).filter(Agendamento.id == agendamento_id).first()
            if not agend:
                return False, "Agendamento não encontrado"

            agend.status = 'cancelado'
            db.commit()
            
            logger.info(f"Agendamento {agendamento_id} cancelado")
            return True, "Agendamento cancelado com sucesso"
        except Exception as e:
            db.rollback()
            logger.error(f"Erro ao cancelar agendamento {agendamento_id}: {e}")
            return False, f"Erro ao cancelar: {str(e)}"
        finally:
            db.close()

    @com_retry
    def obter_dashboard(self) -> Dict:
        """Obtém dados para dashboard"""
        db = SessionLocal()
        try:
            profissionais = db.query(Profissional).filter(Profissional.ativo == True).all()
            
            dados = {
                'profissionais': [],
                'total_agendamentos': 0
            }

            for prof in profissionais:
                agendamentos = db.query(Agendamento).filter(
                    Agendamento.profissional_id == prof.id,
                    Agendamento.status == 'confirmado'
                ).all()

                dados['profissionais'].append({
                    'id': prof.id,
                    'nome': prof.nome,
                    'especialidade': prof.especialidade,
                    'total_agendamentos': len(agendamentos),
                    'ativo': prof.ativo
                })
                dados['total_agendamentos'] += len(agendamentos)

            return dados
        except Exception as e:
            logger.error(f"Erro ao obter dashboard: {e}")
            raise
        finally:
            db.close()

    @staticmethod
    def validar_data(data_str: str) -> bool:
        """Valida formato de data DD/MM/YYYY"""
        try:
            dia, mes, ano = data_str.split('/')
            dia, mes, ano = int(dia), int(mes), int(ano)
            data = date(ano, mes, dia)
            
            # Deve ser future
            if data < date.today():
                return False
                
            # Máximo 30 dias no futuro
            if (data - date.today()).days > 30:
                return False
                
            return True
        except:
            return False

    @staticmethod
    def validar_telefone(telefone: str) -> bool:
        """Valida telefone (10-11 dígitos)"""
        digits = ''.join(filter(str.isdigit, telefone))
        return len(digits) in [10, 11]

    @staticmethod
    def validar_cliente(nome: str) -> bool:
        """Valida nome de cliente"""
        return 3 <= len(nome.strip()) <= 100
