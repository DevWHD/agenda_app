"""
Database Models - SQLAlchemy ORM para Marcia Rocha Beauty
Conecta ao Neon PostgreSQL
"""
import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Date, Time, Boolean, ForeignKey, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    raise ValueError("DATABASE_URL não está configurada. Configure a variável de ambiente DATABASE_URL")

# Criar engine com otimizações
engine = create_engine(
    DATABASE_URL,
    pool_size=20,                          # Aumentado para mais conexões simultâneas
    max_overflow=30,                       # Aumentado para picos de tráfego
    pool_pre_ping=True,                    # Verifica conexão antes de usar
    pool_recycle=3600,                     # Recicla conexões a cada 1 hora
    pool_timeout=30,                       # Timeout ao obter conexão
    echo=False,
    connect_args={
        'connect_timeout': 10,             # Timeout de 10 segundos
        'keepalives': 1,                   # Ativa keep-alive
        'keepalives_idle': 30,             # Envia keep-alive a cada 30s de inatividade
        'keepalives_interval': 10,         # Intervalo entre keep-alives
        'keepalives_count': 5              # Número de keep-alives antes de dar up
    }
)

# SessionLocal para criar sessões
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para declarar modelos
Base = declarative_base()

# ============================================================
# MODELOS ORM
# ============================================================

class Profissional(Base):
    __tablename__ = "profissionais"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False)
    especialidade = Column(String(255))
    dias_uteis = Column(ARRAY(String), nullable=True)
    intervalo_entre_clientes = Column(Integer, default=10)
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime, default=datetime.utcnow)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relações
    procedimentos = relationship("Procedimento", back_populates="profissional", cascade="all, delete-orphan")
    agendamentos = relationship("Agendamento", back_populates="profissional", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'especialidade': self.especialidade,
            'dias_uteis': self.dias_uteis,
            'intervalo_entre_clientes': self.intervalo_entre_clientes,
            'ativo': self.ativo
        }


class Procedimento(Base):
    __tablename__ = "procedimentos"

    id = Column(Integer, primary_key=True, index=True)
    profissional_id = Column(Integer, ForeignKey('profissionais.id', ondelete='CASCADE'), nullable=False)
    codigo = Column(String(10), nullable=False)
    nome = Column(String(255), nullable=False)
    descricao = Column(Text)
    preco = Column(String(10))  # DECIMAL como String para compatibilidade
    duracao_minutos = Column(Integer, default=30)
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime, default=datetime.utcnow)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relações
    profissional = relationship("Profissional", back_populates="procedimentos")
    agendamentos = relationship("Agendamento", back_populates="procedimento")

    def to_dict(self):
        return {
            'id': self.id,
            'codigo': self.codigo,
            'nome': self.nome,
            'descricao': self.descricao,
            'preco': self.preco,
            'duracao_minutos': self.duracao_minutos
        }


class Agendamento(Base):
    __tablename__ = "agendamentos"

    id = Column(Integer, primary_key=True, index=True)
    codigo_agendamento = Column(String(20), unique=True, nullable=False)
    profissional_id = Column(Integer, ForeignKey('profissionais.id', ondelete='CASCADE'), nullable=False)
    procedimento_id = Column(Integer, ForeignKey('procedimentos.id', ondelete='CASCADE'), nullable=False)
    cliente_nome = Column(String(255), nullable=False)
    cliente_telefone = Column(String(20), nullable=False)
    cliente_email = Column(String(255))
    data_agendamento = Column(Date, nullable=False, index=True)
    hora_inicio = Column(Time, nullable=False)
    hora_fim = Column(Time)
    status = Column(String(50), default='confirmado')  # confirmado, cancelado, concluido
    notas = Column(Text)
    criado_em = Column(DateTime, default=datetime.utcnow)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relações
    profissional = relationship("Profissional", back_populates="agendamentos")
    procedimento = relationship("Procedimento", back_populates="agendamentos")
    mensagens = relationship("MensagemWhatsApp", back_populates="agendamento")

    def to_dict(self):
        return {
            'id': self.id,
            'codigo_agendamento': self.codigo_agendamento,
            'profissional_id': self.profissional_id,
            'procedimento_id': self.procedimento_id,
            'cliente_nome': self.cliente_nome,
            'cliente_telefone': self.cliente_telefone,
            'cliente_email': self.cliente_email,
            'data_agendamento': self.data_agendamento.strftime('%d/%m/%Y') if self.data_agendamento else None,
            'hora_inicio': self.hora_inicio.strftime('%H:%M') if self.hora_inicio else None,
            'hora_fim': self.hora_fim.strftime('%H:%M') if self.hora_fim else None,
            'status': self.status,
            'notas': self.notas
        }


class Feriado(Base):
    __tablename__ = "feriados"

    id = Column(Integer, primary_key=True, index=True)
    data = Column(Date, unique=True, nullable=False)
    descricao = Column(String(255))
    criado_em = Column(DateTime, default=datetime.utcnow)


class HorarioFuncionamento(Base):
    __tablename__ = "horario_funcionamento"

    id = Column(Integer, primary_key=True, index=True)
    dia_semana = Column(String(20), unique=True, nullable=False)
    hora_abertura = Column(Time)
    hora_fechamento = Column(Time)
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime, default=datetime.utcnow)


class MensagemWhatsApp(Base):
    __tablename__ = "mensagens_whatsapp"

    id = Column(Integer, primary_key=True, index=True)
    telefone_usuario = Column(String(20), nullable=False, index=True)
    mensagem_enviada = Column(Text)
    mensagem_recebida = Column(Text)
    tipo = Column(String(50))  # texto, agendamento, cancelamento, menu
    agendamento_id = Column(Integer, ForeignKey('agendamentos.id', ondelete='SET NULL'))
    criado_em = Column(DateTime, default=datetime.utcnow, index=True)

    # Relações
    agendamento = relationship("Agendamento", back_populates="mensagens")


def get_db():
    """Dependency para obter sessão do banco"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def verificar_conexao_banco() -> bool:
    """Verifica se a conexão com o banco está ok"""
    try:
        db = SessionLocal()
        db.execute('SELECT 1')
        db.close()
        return True
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Erro ao conectar no banco de dados: {e}")
        return False


def executar_com_retry(funcao, max_tentativas=3):
    """Executa uma função com retry em caso de erro de conexão"""
    import time
    import logging
    logger = logging.getLogger(__name__)
    
    for tentativa in range(max_tentativas):
        try:
            return funcao()
        except Exception as e:
            if tentativa < max_tentativas - 1:
                tempo_espera = 2 ** tentativa  # Exponential backoff
                logger.warning(f"Erro na tentativa {tentativa + 1}/{max_tentativas}: {e}. Tentando novamente em {tempo_espera}s...")
                time.sleep(tempo_espera)
            else:
                logger.error(f"Falha após {max_tentativas} tentativas: {e}")
                raise
        db.close()


def init_db():
    """Inicializar banco de dados (criar tabelas se não existirem)"""
    Base.metadata.create_all(bind=engine)
    print("✅ Banco de dados inicializado!")
