"""
WSGI application entry point
Alternative entry point for some deployment platforms
"""
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Importar a aplicação Flask
from app import app

if __name__ == "__main__":
    app.run()
