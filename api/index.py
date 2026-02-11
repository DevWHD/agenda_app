"""
Entry point para Vercel
Importa a app Flask do app.py e a expõe para o Vercel
"""
import sys
import os

# Adicionar o diretório pai ao path para importar módulos
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar a app Flask
from app import app

# Exportar para Vercel
__all__ = ['app']
