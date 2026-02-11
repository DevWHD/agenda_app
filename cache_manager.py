"""
Cache em memória com TTL (Time To Live)
Melhora performance diminuindo queries ao banco
"""
import time
from functools import wraps
from typing import Any, Callable, Dict, Tuple

class CacheSimples:
    def __init__(self, ttl_segundos: int = 300):
        self.cache: Dict[str, Tuple[Any, float]] = {}
        self.ttl = ttl_segundos
    
    def obter(self, chave: str) -> Any:
        """Obtém valor do cache se ainda estiver válido"""
        if chave not in self.cache:
            return None
        
        valor, timestamp = self.cache[chave]
        tempo_decorrido = time.time() - timestamp
        
        if tempo_decorrido > self.ttl:
            del self.cache[chave]
            return None
        
        return valor
    
    def definir(self, chave: str, valor: Any) -> None:
        """Define valor do cache com timestamp atual"""
        self.cache[chave] = (valor, time.time())
    
    def limpar(self, chave: str = None) -> None:
        """Limpa cache - especifica chave ou limpa tudo"""
        if chave:
            self.cache.pop(chave, None)
        else:
            self.cache.clear()

# Instâncias de cache para diferentes dados
cache_profissionais = CacheSimples(ttl_segundos=300)  # 5 minutos
cache_procedimentos = CacheSimples(ttl_segundos=300)   # 5 minutos
cache_dashboard = CacheSimples(ttl_segundos=60)        # 1 minuto (mais dinâmico)

def cache_decorator(tempo_ttl: int = 300):
    """Decorator para cachear resultado de funções"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Criar chave única baseada em função, args e kwargs
            chave = f"{func.__name__}_{str(args)}_{str(kwargs)}"
            
            # Tentar obter do cache simples
            resultado_em_cache = cache_profissionais.obter(chave)
            if resultado_em_cache is not None:
                return resultado_em_cache
            
            # Se não estiver em cache, executar função
            resultado = func(*args, **kwargs)
            cache_profissionais.definir(chave, resultado)
            return resultado
        
        return wrapper
    return decorator

# Funções utilitárias de cache
def limpar_cache_procedimentos():
    """Limpar cache de procedimentos quando há mudança"""
    cache_profissionais.limpar()
    cache_procedimentos.limpar()

def limpar_cache_dashboard():
    """Limpar apenas cache do dashboard"""
    cache_dashboard.limpar()

def limpar_todo_cache():
    """Limpar todo o cache"""
    cache_profissionais.limpar()
    cache_procedimentos.limpar()
    cache_dashboard.limpar()
