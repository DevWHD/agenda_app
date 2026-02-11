"""
Configuração de Logging para aplicação
Centraliza logging com múltiplos handlers
"""
import logging
import logging.handlers
import os
from datetime import datetime

def configurar_logging(nivel=logging.INFO, arquivo_log='logs/app.log'):
    """
    Configura sistema de logging da aplicação
    
    Args:
        nivel: Nível de logging (DEBUG, INFO, WARNING, ERROR)
        arquivo_log: Caminho do arquivo de log
    """
    
    # Criar diretório de logs se não existir
    os.makedirs(os.path.dirname(arquivo_log) or 'logs', exist_ok=True)
    
    # Root logger
    logger = logging.getLogger()
    logger.setLevel(nivel)
    
    # Formato com mais detalhes
    formato = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler para console (sempre)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(nivel)
    console_handler.setFormatter(formato)
    logger.addHandler(console_handler)
    
    # Handler para arquivo com rotação
    try:
        file_handler = logging.handlers.RotatingFileHandler(
            arquivo_log,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5            # 5 arquivos antigos
        )
        file_handler.setLevel(logging.DEBUG)  # Arquivo sempre tem DEBUG
        file_handler.setFormatter(formato)
        logger.addHandler(file_handler)
        print(f"✅ Logging em arquivo: {arquivo_log}")
    except Exception as e:
        print(f"⚠️ Erro ao configurar logging em arquivo: {e}")
    
    # Handler para erros críticos (arquivo separado)
    try:
        error_handler = logging.handlers.RotatingFileHandler(
            'logs/error.log',
            maxBytes=5*1024*1024,   # 5MB
            backupCount=3            # 3 arquivos antigos
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formato)
        logger.addHandler(error_handler)
    except Exception as e:
        print(f"⚠️ Erro ao configurar error logging: {e}")
    
    logger.info("=" * 60)
    logger.info("📋 Sistema de Logging Configurado")
    logger.info(f"   Nível: {logging.getLevelName(nivel)}")
    logger.info(f"   Arquivo: {arquivo_log}")
    logger.info(f"   Início: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)

if __name__ == "__main__":
    # Teste de logging
    configurar_logging(nivel=logging.DEBUG)
    logger = logging.getLogger(__name__)
    
    logger.debug("Mensagem DEBUG")
    logger.info("Mensagem INFO")
    logger.warning("Mensagem WARNING")
    logger.error("Mensagem ERROR")
    logger.critical("Mensagem CRITICAL")
    
    print("\n✅ Teste de logging completo!")
