"""
Configuração de Produção para Agenda App
Use estas configurações ao fazer deploy em produção
"""

import os
from dotenv import load_dotenv

load_dotenv()

class ConfigProducao:
    """Configuração para ambiente de produção"""
    
    # Flask
    FLASK_ENV = "production"
    FLASK_DEBUG = False
    TESTING = False
    
    # Database  
    SQLALCHEMY_ECHO = False  # Não fazer log de SQL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Pool de Conexões (ajustado para produção)
    DATABASE_POOL_SIZE = 50          # Mais conexões
    DATABASE_MAX_OVERFLOW = 50       # Mais conexões extras
    DATABASE_POOL_TIMEOUT = 30       # Esperar 30s
    DATABASE_POOL_RECYCLE = 3600     # Reciclar a cada 1h
    
    # Cache
    CACHE_TTL = 300                 # 5 minutos
    CACHE_DASHBOARD_TTL = 60        # 1 minuto (mais dinâmico)
    
    # Logging
    LOG_LEVEL = "WARNING"           # Menos verboso em produção
    LOG_FILE = "/var/log/agenda_app/app.log"
    
    # API
    JSON_SORT_KEYS = False
    JSONIFY_PRETTYPRINT_REGULAR = False  # Não pretty-print
    
    # CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')
    CORS_ALLOW_HEADERS = ['Content-Type', 'Authorization']
    CORS_ALLOW_METHODS = ['GET', 'POST', 'DELETE', 'OPTIONS']
    CORS_SUPPORTS_CREDENTIALS = True
    
    # Segurança
    SESSION_COOKIE_SECURE = True     # HTTPS only
    SESSION_COOKIE_HTTPONLY = True   # Não acessível via JS
    SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection
    
    # Timeout
    PROPAGATE_EXCEPTIONS = True
    JSON_SORT_KEYS = False
    EXPLAIN_TEMPLATE_LOADING = False


class ConfigDesenvolvimento:
    """Configuração para desenvolvimento"""
    
    # Flask
    FLASK_ENV = "development"
    FLASK_DEBUG = True
    TESTING = False
    
    # Database
    SQLALCHEMY_ECHO = True   # Log toda SQL
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    
    # Pool de Conexões (menor para dev)
    DATABASE_POOL_SIZE = 5
    DATABASE_MAX_OVERFLOW = 10
    DATABASE_POOL_TIMEOUT = 10
    DATABASE_POOL_RECYCLE = 3600
    
    # Cache
    CACHE_TTL = 60          # 1 minuto em dev
    CACHE_DASHBOARD_TTL = 10  # 10 segundos
    
    # Logging
    LOG_LEVEL = "DEBUG"     # Tudo
    LOG_FILE = "logs/app.log"
    
    # CORS
    CORS_ORIGINS = '*'      # Aceitar tudo em dev
    

class ConfigTeste:
    """Configuração para testes"""
    
    TESTING = True
    FLASK_DEBUG = True
    DATABASE_URL = 'sqlite:///:memory:'
    
    # Cache desabilitado em testes
    CACHE_TTL = 0
    

# Selecionar configuração baseado em variável de ambiente
AMBIENTE = os.getenv('FLASK_ENV', 'development').lower()

if AMBIENTE == 'production':
    config = ConfigProducao
elif AMBIENTE == 'testing':
    config = ConfigTeste
else:
    config = ConfigDesenvolvimento


# Print configuração ativa (se rodando como script)
if __name__ == "__main__":
    print(f"\n{'='*60}")
    print(f"Configuração Ativa: {AMBIENTE.upper()}")
    print(f"{'='*60}")
    
    import inspect
    for chave, valor in inspect.getmembers(config):
        if not chave.startswith('_'):
            print(f"  {chave}: {valor}")
    
    print(f"{'='*60}\n")
